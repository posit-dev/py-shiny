from typing import TYPE_CHECKING, Any, Sequence, cast, overload

from htmltools import Tag

from .. import reactive
from ..session import Session, get_current_session, require_active_session
from ..ui import output_chat
from ._chat_types import (
    ChatMessage,
    ChatMessageChunk,
    normalize_message,
    normalize_message_chunk,
)
from .renderer import Jsonifiable, Renderer, ValueFn

__all__ = ("Chat", "ChatMessage", "chat")

if TYPE_CHECKING:
    from ._chat_types import AppendMessage, AppendMessageChunk, AppendMessageStream


class Chat:
    def __init__(
        self,
        *,
        # TODO: maybe we can provide a richer experience if we know the client?
        # client: "Client",
        messages: Sequence[ChatMessage] = (),
        # Unfortunately, anthropic wants prompt in the .create() method, which we don't
        # currently support wrap
        # system_prompt: Optional[str] = None,
        placeholder: str = "Enter a message...",
        width: str = "min(680px, 100%)",
        fill: bool = True,
    ):
        self.messages = messages
        self.placeholder = placeholder
        self.width = width
        self.fill = fill


class chat(Renderer[Chat]):
    _session: Session | None  # Do not use. Use `_get_session()` instead
    _messages: reactive.Value[Sequence[ChatMessage]]
    _final_message: str = ""

    def __init__(self, fn: ValueFn[Chat]):
        # MUST be done before super().__init__ is called as `_set_output_metadata` is
        # called in `super().__init__` during auto registration of the output
        self._session = get_current_session()

        super().__init__(fn)

        # Initialize server-side reactives
        self._messages = reactive.Value(())
        self._final_message = ""

    async def render(self) -> Jsonifiable:
        # Reset server-side reactives
        self._messages.set(())
        self._final_message = ""

        value = await self.fn()
        if value is None:
            return None

        self._append_messages(value.messages)

        return {
            "messages": cast(Jsonifiable, value.messages),
            "placeholder": value.placeholder,
            "width": value.width,
            "fill": value.fill,
        }

    # Reactive read of the user input (only changes on submit)
    def user_input(self) -> str:
        input = self._get_session().input
        id = f"{self.output_id}_user_input"
        val = input[id]()
        return cast(str, val)

    # All current messages in the chat box
    def messages(self) -> Sequence[ChatMessage]:
        from .. import req

        # User input causes invalidation of the messages reactive
        user = req(self.user_input())
        user_msg: ChatMessage = {"content": user, "role": "user"}

        # Add the user message to the messages
        self._append_message(user_msg)

        return self._messages()

    # Append a message to the chat box
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

        if chunk:
            # TODO: check if typing will actually yell this is something else than a message chunk
            message = cast("AppendMessageChunk", message)
            msg = normalize_message_chunk(message)
            self._append_message_chunk(msg)
        else:
            message = cast("AppendMessage", message)
            msg = normalize_message(message)
            self._append_message(msg)

        msg_type = "shiny-chat-append-message"
        if chunk:
            msg_type += "-chunk"
        await self._send_custom_message(msg_type, {**msg})

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
        with reactive.isolate():
            msgs = tuple(self._messages()) + tuple(messages)
            self._messages.set(msgs)

    async def _send_custom_message(self, handler: str, obj: dict[str, Any]):
        session = self._get_session()
        id = session.ns(self.output_id)
        await session.send_custom_message(
            "shinyChatMessage",
            {
                "id": id,
                "handler": handler,
                "obj": obj,
            },
        )

    def auto_output_ui(self) -> Tag:
        return output_chat(id=self.output_id)

    def _set_output_metadata(self, *, output_id: str) -> None:
        super()._set_output_metadata(output_id=output_id)

        # Verify that the session used (during `__init__`) when creating the renderer is
        # the same session used when executing the renderer. This is to prevent a user
        # from creating a renderer in one module and registering it on an output with a
        # different session.
        active_session = require_active_session(None)
        if self._get_session() != active_session:
            raise RuntimeError(
                "The session used when creating the renderer "
                "is not the same session used when executing the renderer. "
                "Please file an issue on "
                "GitHub <https://github.com/posit-dev/py-shiny/issues/new> "
                "with an example of how you are reproducing this error. "
                "We would be curious to know your use case!"
            )

    def _get_session(self) -> Session:
        if self._session is None:
            raise RuntimeError(
                "`@render.chat` must be used in a active session context "
                "(i.e., `session.get_current_session()` can't be `None`)."
            )
        return self._session
