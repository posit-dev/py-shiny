from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Generic,
    Iterable,
    Literal,
    Optional,
    Sequence,
    TypeVar,
    cast,
)

from htmltools import Tag

from .. import _utils, reactive
from .._namespaces import resolve_id
from ..session import Session, require_active_session, session_context
from ..types import NotifyException
from ._chat_types import (
    ChatMessage,
    ChatMessageChunk,
    normalize_message,
    normalize_message_chunk,
)
from ._html_deps_py_shiny import chat_deps
from .fill import as_fill_item, as_fillable_container

__all__ = ("Chat", "chat_ui", "ChatMessage", "ChatMessageChunk")

T = TypeVar("T")

SubmitFunction = Callable[[], None]
SubmitFunctionAsync = Callable[[], Awaitable[None]]


class Chat(Generic[T]):
    """
    Initialize a chat session.
    """

    def __init__(
        self,
        id: str,
        *,
        messages: Sequence[ChatMessage] = (),
        session: Optional[Session] = None,
    ):
        self.id = id
        self._messages_init = messages
        self._session = require_active_session(session)

        # Chunked messages get accumulated (using this property) before changing state
        self._final_message = ""

        # Keep track of effects so we can destroy them when the chat is destroyed
        self._effects: list[reactive.Effect_] = []

        with session_context(self._session):
            # Initialize message state
            self._messages: reactive.Value[Sequence[ChatMessage]] = reactive.Value(())

            # Reflect the message state in the UI
            for msg in self._messages_init:
                _utils.run_coro_sync(self.append_message(msg))

            # When user input is submitted, append it to message state
            @reactive.effect
            @reactive.event(self.user_input)
            def append_user_input():
                from .. import req

                input = req(self.user_input())
                user_msg = ChatMessage(content=input, role="user")
                self._append_message(user_msg)

            self._effects.append(append_user_input)

    def ui(
        self,
        placeholder: str = "Enter a message...",
        width: str = "min(680px, 100%)",
        fill: bool = True,
    ) -> Tag:
        if not _express_is_active():
            raise RuntimeError(
                "The `ui()` method of the `ui.Chat` class only works in a Shiny Express context."
                " Use `ui.chat_ui()` instead in Shiny Core to locate the chat UI."
            )
        return chat_ui(
            id=self.id,
            placeholder=placeholder,
            width=width,
            fill=fill,
        )

    def on_user_submit(
        self,
        fn: SubmitFunction | SubmitFunctionAsync | None = None,
        *,
        error: Literal["sanitize", "actual", "unhandled"] = "sanitize",
    ) -> (
        reactive.Effect_
        | Callable[[SubmitFunction | SubmitFunctionAsync], reactive.Effect_]
    ):
        """
        Register a callback to run when the user submits a message.
        """

        def create_effect(fn: SubmitFunction | SubmitFunctionAsync):
            afunc = _utils.wrap_async(fn)

            @reactive.effect
            @reactive.event(self.user_input)
            async def handle_user_input():
                if error == "unhandled":
                    await afunc()
                else:
                    try:
                        await afunc()
                    except Exception as e:
                        await self._remove_loading_message()
                        raise NotifyException(str(e), sanitize=error == "sanitize")

            self._effects.append(handle_user_input)

            return handle_user_input

        if fn is None:
            return create_effect
        else:
            return create_effect(fn)

    def user_input(self) -> str:
        """
        Reactively read user input

        Most users will want to use `on_user_submit` instead of reading this directly.
        """

        id = f"{self.id}_user_input"
        val = self._session.input[id]()
        return cast(str, val)

    def messages(self) -> Sequence[ChatMessage]:
        """
        Reactively read chat messages
        """
        return self._messages()

    async def append_message(self, message: Any, *, chunk: bool = False) -> None:
        """
        Append a message to the chat.
        """

        if chunk:
            msg = normalize_message_chunk(message)
            self._append_message_chunk(msg)
        else:
            msg = normalize_message(message)
            self._append_message(msg)

        if msg["role"] != "assistant":
            raise ValueError("Only assistant messages can be appended to the chat. ")

        # print(msg)

        msg_type = "shiny-chat-append-message"
        if chunk:
            msg_type += "-chunk"
        await self._send_custom_message(msg_type, msg)
        # TODO: Joe said it's a good idea to yield here, but I'm not sure why?
        # await asyncio.sleep(0)

    async def append_message_stream(self, message: Iterable[Any] | AsyncIterable[Any]):
        message = _utils.wrap_async_iterable(message)

        @reactive.extended_task
        async def _do_stream():
            await self._append_message_stream(message)

        _do_stream()

    async def _append_message_stream(self, message: AsyncIterable[Any]):
        # Get the first message just to determine the role
        miter = message.__aiter__()
        msg_first = await miter.__anext__()
        role = normalize_message_chunk(msg_first)["role"]

        # Start the message
        msg_start = ChatMessageChunk(content="", type="message_start", role=role)
        await self.append_message(msg_start, chunk=True)

        try:
            async for msg in message:
                msg = normalize_message_chunk(msg)
                await self.append_message(msg, chunk=True)
        finally:
            msg_end = ChatMessageChunk(content="", type="message_end", role=role)
            await self.append_message(msg_end, chunk=True)

    # For chunk messages, accumulate the chunks until we have a signal that the message
    # has ended
    def _append_message_chunk(self, msg: ChatMessageChunk):
        self._final_message += msg["content"]
        if "type" in msg and msg["type"] == "message_end":
            final = ChatMessage(content=self._final_message, role=msg["role"])
            self._append_message(final)
            self._final_message = ""

    def _append_message(self, message: ChatMessage):
        self._append_messages((message,))

    def _append_messages(self, messages: Sequence[ChatMessage]):
        with reactive.isolate():
            msgs = tuple(self._messages()) + tuple(messages)

        self._messages.set(msgs)

    async def clear_messages(self):
        """
        Clear all messages in the chat.
        """
        self._messages.set(())
        await self._send_custom_message("shiny-chat-clear-messages", None)

    def destroy(self):
        """
        Destroy the chat instance.
        """
        for x in self._effects:
            x.destroy()

    async def _remove_loading_message(self):
        await self._send_custom_message("shiny-chat-remove-loading-message", None)

    async def _send_custom_message(
        self, handler: str, obj: ChatMessage | ChatMessageChunk | None
    ):
        await self._session.send_custom_message(
            "shinyChatMessage",
            {
                "id": self.id,
                "handler": handler,
                "obj": obj,
            },
        )


def chat_ui(
    id: str,
    placeholder: str = "Enter a message...",
    width: str = "min(680px, 100%)",
    fill: bool = True,
) -> Tag:
    """
    Create a chat UI component.
    """

    id = resolve_id(id)

    res = Tag(
        "shiny-chat-container",
        chat_deps(),
        {"style": f"width: {width}"},
        id=id,
        placeholder=placeholder,
        fill=fill,
    )

    if fill:
        res = as_fillable_container(as_fill_item(res))

    return res


def _express_is_active() -> bool:
    from ..express._run import get_top_level_recall_context_manager

    try:
        get_top_level_recall_context_manager()
        return True
    except RuntimeError:
        return False
