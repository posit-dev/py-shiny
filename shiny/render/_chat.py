import json
from typing import Any, Literal, Sequence, cast

from htmltools import Tag
from openai.types.chat import ChatCompletionMessageParam

from .. import reactive
from ..session import Session, get_current_session, require_active_session
from ..ui import output_chat
from .renderer import Jsonifiable, Renderer, ValueFn

__all__ = ("Chat", "ChatMessage", "chat")

Roles = Literal["assistant", "user", "system"]

# TODO: for some reason this isn't compatible with openai's type?
# class ChatMessage(TypedDict):
#     content: str
#     role: Roles

ChatMessage = ChatCompletionMessageParam


class Chat:
    def __init__(
        self,
        *,
        messages: Sequence[ChatMessage],
        # style: Literal["default", "messager"] = "default",
        # icons: Sequence[Literal["copy", "refresh"]] = ("copy", ),
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

    def __init__(self, fn: ValueFn[Chat]):
        # MUST be done before super().__init__ is called as `_set_output_metadata` is
        # called in `super().__init__` during auto registration of the output
        self._session = get_current_session()

        super().__init__(fn)

        # Initialize server-side reactives
        self._messages = reactive.Value(())

    async def render(self) -> Jsonifiable:
        # Reset server-side reactives
        self._messages.set(())

        value = await self.fn()
        if value is None:
            return None

        self._messages.set(value.messages)

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

        # Append the user message to the messages reactive
        with reactive.isolate():
            msgs = tuple(self._messages()) + (user_msg,)
            self._messages.set(msgs)

        return self._messages()

    # Append a message to the chat box
    async def append_message(
        self, content: str, *, role: Roles = "assistant", stream: bool = False
    ):

        msg = cast(ChatMessage, {"content": content, "role": role})

        with reactive.isolate():
            msgs = tuple(self._messages()) + (msg,)
            self._messages.set(msgs)

        type = "shiny-chat-append-message"
        if stream:
            type += "-stream"
        await self._send_custom_message(
            type,
            {**msg, "stream": stream},
        )

    # Replace a message in the chat box
    # async def replace_message(
    #    self,
    #    *,
    #    index: int,
    #    content: str,
    #    role: Roles = "assistant",
    #    stream: bool = False,
    # ):
    #
    #    type = "shiny-chat-replace-message"
    #    if stream:
    #        type += "-stream"
    #    await self._send_custom_message(
    #        type,
    #        {
    #            "index": index,
    #            "content": content,
    #            "role": role,
    #            "stream": stream,
    #        },
    #    )

    # TODO: if refresh icon is clicked, report the message index that needs to be replaced
    # def message_invalidated():
    #     pass

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
