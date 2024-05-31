import sys
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

from .. import _utils, reactive, ui
from .._app import SANITIZE_ERROR_MSG
from .._namespaces import resolve_id
from ..session import Session, require_active_session, session_context
from ._chat_types import (
    ChatMessage,
    ChatMessageChunk,
    normalize_message,
    normalize_message_chunk,
)
from ._html_deps_py_shiny import autoresize_dependency, chat_deps
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
        client: Optional[T] = None,
        session: Optional[Session] = None,
    ):
        self.id = id
        self.client = client
        self._session = require_active_session(session)

        # Chunked messages get accumulated (using this property) before changing state
        self._final_message = ""

        with session_context(self._session):
            # Initialize message state
            self._messages: reactive.Value[Sequence[ChatMessage]] = reactive.Value(())

            # When user input is submitted, append it to message state
            @reactive.effect
            @reactive.event(self.user_input)
            def _():
                from .. import req

                input = req(self.user_input())
                user_msg = ChatMessage(content=input, role="user")
                self._append_message(user_msg)

    def tagify(self) -> Tag:
        return self.__call__()

    def __call__(
        self,
        messages: Sequence[ChatMessage] = (),
        placeholder: str = "Enter a message...",
        width: str = "min(680px, 100%)",
        fill: bool = True,
    ) -> Tag:
        if not self._is_express():
            raise RuntimeError(
                "The `__call__()` method of the `ui.Chat` class only works in a Shiny Express context."
                " Use `ui.chat_ui()` instead in Shiny Core to locate the chat UI."
            )
        return chat_ui(
            id=self.id,
            messages=messages,
            placeholder=placeholder,
            width=width,
            fill=fill,
        )

    # TODO: maybe this should be a utility function in express?
    @staticmethod
    def _is_express() -> bool:
        from ..express._run import get_top_level_recall_context_manager

        try:
            get_top_level_recall_context_manager()
            return True
        except RuntimeError:
            return False

    def on_user_submit(
        self,
        func: SubmitFunction | SubmitFunctionAsync,
        errors: Literal["sanitize", "show", "none"] = "sanitize",
    ) -> reactive.Effect_:
        """
        Register a callback to run when the user submits a message.
        """

        afunc = _utils.wrap_async(func)

        @reactive.effect
        @reactive.event(self.user_input)
        async def wrapper():
            try:
                await afunc()
            # TODO: does this handle req() correctly?
            except Exception as e:
                if errors == "sanitize":
                    ui.notification_show(
                        SANITIZE_ERROR_MSG, type="error", duration=5000
                    )
                elif errors == "show":
                    ui.notification_show(
                        ui.markdown(str(e)), type="error", duration=5000
                    )

                raise e

        return wrapper

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
        if sys.version_info < (3, 10):
            # ater/anext were new in 3.10
            raise RuntimeError("append_message_stream() requires Python 3.10 or later")

        msg_iter = aiter(message)

        # Start the message
        msg_start = await anext(msg_iter)
        msg_start = normalize_message_chunk(msg_start)
        if msg_start.get("type", None) is None:
            msg_start["type"] = "message_start"
        await self.append_message(msg_start, chunk=True)

        # Append all the chunks (and end the message when we reach the end)
        while True:
            try:
                msg = await anext(msg_iter)
                await self.append_message(msg, chunk=True)
            except StopAsyncIteration:
                msg = ChatMessageChunk(
                    content="",
                    role="assistant",
                    type="message_end",
                )
                await self.append_message(msg, chunk=True)
                break

    # For chunk messages, accumulate the chunks until we have a signal that the message
    # has ended
    def _append_message_chunk(self, msg: ChatMessageChunk):
        self._final_message += msg["content"]
        if "type" in msg and msg["type"] == "message_end":
            final = ChatMessage(content=self._final_message, role="assistant")
            self._append_message(final)
            self._final_message = ""

    def _append_message(self, message: ChatMessage):
        self._append_messages((message,))

    def _append_messages(self, messages: Sequence[ChatMessage]):
        with reactive.isolate():
            msgs = tuple(self._messages()) + tuple(messages)
            self._messages.set(msgs)

    async def clear_messages(self):
        with reactive.isolate():
            self._messages.set(())

        await self._send_custom_message("shiny-chat-clear-messages", None)

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
    messages: Sequence[ChatMessage] = (),
    placeholder: str = "Enter a message...",
    width: str = "min(680px, 100%)",
    fill: bool = True,
) -> Tag:
    """
    Create a chat UI component.
    """

    messages_tag = Tag(
        "shiny-chat-messages",
        *[
            Tag(
                "shiny-chat-message",
                content=x["content"],
                role=x["role"],
            )
            for x in messages
        ],
    )

    if fill:
        messages_tag = as_fill_item(messages_tag)

    id = resolve_id(id)

    res = Tag(
        "shiny-chat-container",
        chat_deps(),
        messages_tag,
        Tag(
            "shiny-chat-input",
            autoresize_dependency(),
            placeholder=placeholder,
            id=f"{id}_user_input",
        ),
        {"style": f"width: {width}"},
        id=id,
    )

    if fill:
        res = as_fillable_container(as_fill_item(res))

    return res
