from typing import TYPE_CHECKING, Any, Iterable, Literal, TypedDict, cast

from typing_extensions import NotRequired

Role = Literal["assistant", "user", "system"]


class ChatMessage(TypedDict):
    content: str
    role: Role


class ChatMessageChunk(TypedDict):
    content: str
    role: Literal["assistant"]
    type: NotRequired[Literal["message_start", "message_chunk", "message_end"]]


if TYPE_CHECKING:
    from anthropic import Stream as AnthropicStream
    from anthropic.types import Message as AnthropicMessage
    from anthropic.types import MessageStreamEvent
    from google.generativeai.types.generation_types import (  # pyright: ignore[reportMissingTypeStubs]
        GenerateContentResponse,
    )
    from openai import Stream as OpenAIStream
    from openai.types.chat import ChatCompletion, ChatCompletionChunk

    AppendMessage = (
        ChatCompletion
        | AnthropicMessage
        | GenerateContentResponse
        | ChatMessage
        | str
        | None
    )
    AppendMessageStream = (
        OpenAIStream[ChatCompletionChunk]
        | AnthropicStream[MessageStreamEvent]
        | GenerateContentResponse
        | Iterable[ChatMessageChunk]
        | Iterable[str | None]
    )
    AppendMessageChunk = (
        ChatCompletionChunk
        | MessageStreamEvent
        | GenerateContentResponse
        | ChatMessageChunk
        | str
        | None
    )


def normalize_message(message: "AppendMessage") -> ChatMessage:
    if message is None:
        message = ""

    if isinstance(message, str):
        return {"content": message, "role": "assistant"}

    if is_openai_message(message):
        msg = cast("ChatCompletion", message)
        content = msg.choices[0].message.content
        return {"content": content or "", "role": "assistant"}

    if is_anthropic_message(message):
        msg = cast("AnthropicMessage", message)
        content = msg.content[0].text
        return {"content": content, "role": "assistant"}

    if is_google_message(message):
        msg = cast("GenerateContentResponse", message)
        content = msg.text
        return {"content": content, "role": "assistant"}

    if isinstance(message, dict):
        if "content" in message and "role" in message:
            return message
        else:
            raise ValueError(
                f"Expected 'content' and 'role' keys in message dict: {message}"
            )

    raise ValueError(f"Invalid message type: {type(message)}. ")


def is_openai_message(message: Any) -> bool:
    try:
        from openai.types.chat import ChatCompletion

        return isinstance(message, ChatCompletion)
    except ImportError:
        return False


def is_anthropic_message(message: Any) -> bool:
    try:
        from anthropic.types import Message

        return isinstance(message, Message)
    except ImportError:
        return False


def is_google_message(message: Any) -> bool:
    try:
        from google.generativeai.types.generation_types import (  # pyright: ignore[reportMissingTypeStubs]
            GenerateContentResponse,
        )

        return isinstance(message, GenerateContentResponse)
    except ImportError:
        return False


def normalize_message_chunk(chunk: "AppendMessageChunk") -> ChatMessageChunk:
    if is_openai_message_chunk(chunk):
        x = cast("ChatCompletionChunk", chunk)
        content = x.choices[0].delta.content
        return normalize_message_chunk_string(content)

    if is_anthropic_message_chunk(chunk):
        res: ChatMessageChunk = {
            "content": "",
            "type": "message_chunk",
            "role": "assistant",
        }
        x = cast("MessageStreamEvent", chunk)
        if x.type == "content_block_start":
            res["type"] = "message_start"
        elif x.type == "content_block_delta":
            res["content"] = x.delta.text

        return res

    if is_google_message_chunk(chunk):
        x = cast("GenerateContentResponse", chunk)
        # I don't think GenerateContentResponse has a formal signal of message start/end?
        return {"content": x.text, "role": "assistant"}

    if isinstance(chunk, dict):
        if "content" in chunk and "role" in chunk and "type" in chunk:
            return chunk
        else:
            raise ValueError(
                f"Expected 'content', 'role', and 'type' keys in message dict: {chunk}"
            )

    raise ValueError(f"Invalid message type: {type(chunk)}. ")


# With no explicit start/stop signal, follow the openai convention of "" to start
# and None to end
def normalize_message_chunk_string(chunk: str | None) -> ChatMessageChunk:
    type = "message_chunk"
    if chunk == "":
        type = "message_start"
    if chunk is None:
        type = "message_end"
        chunk = ""
    return {"content": chunk, "type": type, "role": "assistant"}


def is_openai_message_chunk(x: Any) -> bool:
    try:
        from openai.types.chat import ChatCompletionChunk

        return isinstance(x, ChatCompletionChunk)
    except ImportError:
        return False


def is_anthropic_message_chunk(x: Any) -> bool:
    try:
        from anthropic.types import MessageStreamEvent

        return isinstance(x, MessageStreamEvent)
    except ImportError:
        return False


def is_google_message_chunk(x: Any) -> bool:
    try:
        from google.generativeai.types.generation_types import (  # pyright: ignore[reportMissingTypeStubs]
            GenerateContentResponse,
        )

        return isinstance(x, GenerateContentResponse)
    except ImportError:
        return False
