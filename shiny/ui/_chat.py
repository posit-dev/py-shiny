from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Generic,
    Literal,
    Optional,
    Sequence,
    TypeVar,
    cast,
    overload,
)

from htmltools import Tag

from .. import _utils, reactive
from .._namespaces import resolve_id
from ..session import Session, get_current_session
from ._chat_types import (
    ChatMessage,
    ChatMessageChunk,
    normalize_message,
    normalize_message_chunk,
)
from ._html_deps_py_shiny import chat_deps
from .fill import as_fill_item, as_fillable_container

__all__ = ("Chat", "ChatMessage", "ChatMessageChunk")

if TYPE_CHECKING:
    from ._chat_types import AppendMessage, AppendMessageChunk, AppendMessageStream

T = TypeVar("T")

SubmitFunction = Callable[[], None]
SubmitFunctionAsync = Callable[[], Awaitable[None]]


class NoSessionState:
    session: None
    messages: Sequence[ChatMessage]

    def __init__(self, messages: Sequence[ChatMessage]):
        self.session = None
        self.messages = messages


# When there's a session, messages get upgraded to a reactive value
class SessionState:
    session: Session
    messages: reactive.Value[Sequence[ChatMessage]]

    def __init__(
        self, session: Session, messages: reactive.Value[Sequence[ChatMessage]]
    ):
        self.session = session
        self.messages = messages


class Chat(Generic[T]):
    """
    Initialize a chat session.
    """

    def __init__(
        self,
        id: str,
        client: Optional[T] = None,
        *,
        messages: Sequence[ChatMessage] = (),
        # Unfortunately, anthropic wants prompt in the .create() method, so I don't think
        # we can guarantee this'll work as intended (for all models)
        # system_prompt: Optional[str] = None,
        placeholder: str = "Enter a message...",
        width: str = "min(680px, 100%)",
        fill: bool = True,
    ):

        self.id = id
        self.client = client
        self._placeholder = placeholder
        self._width = width
        self._fill = fill

        # Initial message state
        self._messages_init = messages

        # Reactive message state
        # NOTE: don't read this directly, use self._get_session_state() instead
        self._messages: reactive.Value[Sequence[ChatMessage]] | None = None

        # For chunked messages
        self._final_message = ""

    def tagify(self) -> Tag:

        # Can be called with or without an active session
        state = self._get_session_state(require_session=False)
        if isinstance(state, NoSessionState):
            messages = state.messages
        else:
            messages = state.messages()

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

        if self._fill:
            messages_tag = as_fill_item(messages_tag)

        id = resolve_id(self.id)

        res = Tag(
            "shiny-chat-container",
            chat_deps(),
            messages_tag,
            Tag(
                "shiny-chat-input",
                placeholder=self._placeholder,
                id=f"{id}_user_input",
            ),
            {"style": f"width: {self._width}"},
            id=id,
        )

        if self._fill:
            res = as_fillable_container(as_fill_item(res))

        return res

    def on_user_submit(
        self, func: SubmitFunction | SubmitFunctionAsync
    ) -> reactive.Effect_:
        """
        Register a callback to run when the user submits a message.
        """

        self._get_session_state(require_session=True)

        afunc = _utils.wrap_async(func)

        @reactive.effect
        @reactive.event(self.user_input)
        async def wrapper():
            await afunc()

        return wrapper

    def user_input(self) -> str:
        """
        Reactively read user input
        """

        state = self._get_session_state(require_session=True)
        session = state.session

        id = f"{self.id}_user_input"
        val = session.input[id]()
        return cast(str, val)

    def messages(self) -> Sequence[ChatMessage]:
        """
        Reactively read chat messages
        """

        state = self._get_session_state(require_session=True)

        from .. import req

        # User input causes invalidation of the messages reactive
        user = req(self.user_input())
        user_msg: ChatMessage = {"content": user, "role": "user"}

        # Add the user message to the messages
        self._append_message(user_msg)

        return state.messages()

    @overload
    async def append_message(
        self, message: "AppendMessage", *, chunk: bool = False
    ) -> None: ...

    @overload
    async def append_message(
        self, message: "AppendMessageChunk", *, chunk: bool = True
    ) -> None: ...

    async def append_message(
        self, message: "AppendMessage | AppendMessageChunk", *, chunk: bool = False
    ) -> None:
        """
        Append a message to the chat.
        """

        if chunk:
            # TODO: check if typing will actually yell this is something else than a message chunk
            message = cast("AppendMessageChunk", message)
            msg = normalize_message_chunk(message)
            self._append_message_chunk(msg)
        else:
            message = cast("AppendMessage", message)
            msg = normalize_message(message)
            self._append_message(msg)

        # print(msg)

        msg_type = "shiny-chat-append-message"
        if chunk:
            msg_type += "-chunk"
        await self._send_custom_message(msg_type, msg)

    async def append_message_stream(self, message: "AppendMessageStream"):
        msg_iter = iter(message)

        # Start the message
        msg_start = next(msg_iter)
        msg_start = normalize_message_chunk(msg_start)
        if msg_start.get("type", None) is None:
            msg_start["type"] = "message_start"
        await self.append_message(msg_start, chunk=True)

        # Append all the chunks (and end the message when we reach the end)
        while True:
            try:
                msg = next(msg_iter)  # type: ignore
                await self.append_message(msg, chunk=True)
            except StopIteration:
                msg: ChatMessageChunk = {
                    "content": "",
                    "role": "assistant",
                    "type": "message_end",
                }
                await self.append_message(msg, chunk=True)
                break

    # For chunk messages, accumulate the chunks until we have a signal that the message
    # has ended
    def _append_message_chunk(self, msg: ChatMessageChunk):
        self._final_message += msg["content"] or ""
        if "type" in msg and msg["type"] == "message_end":
            final: ChatMessage = {
                "content": self._final_message,
                "role": msg["role"],
            }
            self._append_message(final)
            self._final_message = ""

    def _append_message(self, message: ChatMessage):
        self._append_messages((message,))

    def _append_messages(self, messages: Sequence[ChatMessage]):
        state = self._get_session_state(require_session=True)
        with reactive.isolate():
            msgs = tuple(state.messages()) + tuple(messages)
            state.messages.set(msgs)

    # TODO: implement replace_message

    async def clear_messages(self):
        state = self._get_session_state(require_session=True)
        with reactive.isolate():
            state.messages.set(())

        await self._send_custom_message("shiny-chat-clear-messages", None)

    @overload
    def _get_session_state(self, require_session: Literal[True]) -> SessionState: ...

    @overload
    def _get_session_state(
        self, require_session: Literal[False]
    ) -> SessionState | NoSessionState: ...

    def _get_session_state(
        self, require_session: bool = True
    ) -> SessionState | NoSessionState:
        session = get_current_session()

        if session is not None:
            if session.is_stub_session():
                return NoSessionState(messages=self._messages_init)
            if self._messages is None:
                self._messages = reactive.Value(self._messages_init)
            return SessionState(session, self._messages)

        if not require_session:
            return NoSessionState(messages=self._messages_init)

        # TODO: better error message
        raise ValueError(
            "This function must be called from within an active Shiny session"
        )

    async def _send_custom_message(
        self, handler: str, obj: ChatMessage | ChatMessageChunk | None
    ):
        state = self._get_session_state(require_session=True)
        await state.session.send_custom_message(
            "shinyChatMessage",
            {
                "id": self.id,
                "handler": handler,
                "obj": obj,
            },
        )
