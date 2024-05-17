from typing import Any, Literal, Optional, Sequence, TypedDict, Union, cast

from htmltools import Tag

# TODO: make openai a optional dependency?
from openai import Stream
from openai.types.chat import ChatCompletionChunk

from .. import reactive
from ..session import Session, get_current_session, require_active_session
from ..ui import output_chat
from .renderer import Jsonifiable, Renderer, ValueFn

__all__ = ("Chat", "ChatMessage", "chat")

Role = Literal["assistant", "user", "system"]


# ChatMessage = ChatCompletionMessageParam


class UserMessage(TypedDict):
    content: str
    role: Literal["user"]


class AssistantMessage(TypedDict):
    content: Optional[str]  # delta can be None (to end the message)
    role: Literal["assistant"]


class SystemMessage(TypedDict):
    content: Optional[str]
    role: Literal["system"]


ChatMessage = AssistantMessage | SystemMessage | UserMessage


class Chat:
    def __init__(
        self,
        *,
        messages: Sequence[AssistantMessage | SystemMessage],
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
    _current_message_content: str = ""

    def __init__(self, fn: ValueFn[Chat]):
        # MUST be done before super().__init__ is called as `_set_output_metadata` is
        # called in `super().__init__` during auto registration of the output
        self._session = get_current_session()

        super().__init__(fn)

        # Initialize server-side reactives
        self._messages = reactive.Value(())
        self._current_message_content = ""

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
        user_msg: UserMessage = {"content": user, "role": "user"}

        # Add the user message to the messages
        self._update_messages(user_msg)

        return self._messages()

    # Append a message to the chat box
    async def append_message(
        self, message: ChatMessage | str | None, *, delta: bool = False
    ):

        # TODO: also handle ChatCompletionMessageParam?
        if isinstance(message, str) or message is None:
            msg: ChatMessage = {"content": message, "role": "assistant"}
        else:
            msg = message

        if delta:
            self._current_message_content += msg["content"] or ""
            if msg["content"] is None:  # end of message
                msgFinal: AssistantMessage = {
                    "content": self._current_message_content,
                    "role": msg["role"],  # type: ignore
                }
                self._update_messages(msgFinal)
        else:
            self._current_message_content = msg["content"] or ""
            self._update_messages(msg)

        type = "shiny-chat-append-message"
        if delta:
            type += "-delta"
        await self._send_custom_message(type, {**msg})

    # TODO: can we do this in a truly non-blocking way? Maybe via a ExtendedTask running in a separate thread?
    async def append_message_stream(self, response: Stream[ChatCompletionChunk]):
        for chunk in response:
            content = chunk.choices[0].delta.content
            await self.append_message(content, delta=True)

    def _update_messages(self, message: ChatMessage):
        with reactive.isolate():
            msgs = tuple(self._messages()) + (message,)
            self._messages.set(msgs)

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
