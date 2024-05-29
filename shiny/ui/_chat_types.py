from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Literal, TypedDict

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
    from anthropic.types import Message as AnthropicMessage
    from anthropic.types import MessageStreamEvent
    from google.generativeai.types.generation_types import (  # pyright: ignore[reportMissingTypeStubs]
        GenerateContentResponse,
    )
    from openai.types.chat import ChatCompletion, ChatCompletionChunk


class BaseMessageNormalizer(ABC):
    @staticmethod
    @abstractmethod
    def normalize(message: Any) -> ChatMessage:
        pass

    @staticmethod
    @abstractmethod
    def normalize_chunk(chunk: Any) -> ChatMessageChunk:
        pass

    @staticmethod
    @abstractmethod
    def can_normalize(message: Any) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def can_normalize_chunk(chunk: Any) -> bool:
        pass


class StringNormalizer(BaseMessageNormalizer):
    @staticmethod
    def normalize(message: str | None) -> ChatMessage:
        return ChatMessage(content=message or "", role="assistant")

    # Follow openai's convention of "" for message_start and None for message_end
    @staticmethod
    def normalize_chunk(chunk: str | None) -> ChatMessageChunk:
        type = "message_chunk"
        if chunk == "":
            type = "message_start"
        if chunk is None:
            type = "message_end"
            chunk = ""
        return ChatMessageChunk(content=chunk, type=type, role="assistant")

    @staticmethod
    def can_normalize(message: Any) -> bool:
        return isinstance(message, str) or message is None

    @staticmethod
    def can_normalize_chunk(chunk: Any) -> bool:
        return isinstance(chunk, str) or chunk is None


class DictNormalizer(BaseMessageNormalizer):
    @staticmethod
    def normalize(message: dict[str, Any]) -> ChatMessage:
        if "content" in message and "role" in message:
            return ChatMessage(content=message["content"], role=message["role"])
        else:
            raise ValueError("Message must have 'content' and 'role' keys")

    @staticmethod
    def normalize_chunk(chunk: dict[str, Any]) -> ChatMessageChunk:
        if "content" in chunk and "role" in chunk and "type" in chunk:
            return ChatMessageChunk(
                content=chunk["content"],
                role=chunk["role"],
                type=chunk["type"],
            )
        else:
            raise ValueError("Chunk must have 'content', 'role', and 'type' keys")

    @staticmethod
    def can_normalize(message: Any) -> bool:
        return isinstance(message, dict)

    @staticmethod
    def can_normalize_chunk(chunk: Any) -> bool:
        return isinstance(chunk, dict)


class OpenAINormalizer(BaseMessageNormalizer):
    @staticmethod
    def normalize(message: "ChatCompletion") -> ChatMessage:
        content = message.choices[0].message.content
        return ChatMessage(content=content or "", role="assistant")

    @staticmethod
    def normalize_chunk(chunk: "ChatCompletionChunk") -> ChatMessageChunk:
        content = chunk.choices[0].delta.content
        return StringNormalizer.normalize_chunk(content)

    @staticmethod
    def can_normalize(message: Any) -> bool:
        try:
            from openai.types.chat import ChatCompletion

            return isinstance(message, ChatCompletion)
        except ImportError:
            return False

    @staticmethod
    def can_normalize_chunk(chunk: Any) -> bool:
        try:
            from openai.types.chat import ChatCompletionChunk

            return isinstance(chunk, ChatCompletionChunk)
        except ImportError:
            return False


class AnthropicNormalizer(BaseMessageNormalizer):
    @staticmethod
    def normalize(message: "AnthropicMessage") -> ChatMessage:
        content = message.content[0].text
        return {"content": content, "role": "assistant"}

    @staticmethod
    def normalize_chunk(chunk: "MessageStreamEvent") -> ChatMessageChunk:
        content = chunk.delta.text if chunk.type == "content_block_delta" else ""
        type = (
            "message_start" if chunk.type == "content_block_start" else "message_chunk"
        )
        return ChatMessageChunk(content=content, type=type, role="assistant")

    @staticmethod
    def can_normalize(message: Any) -> bool:
        try:
            from anthropic.types import Message as AnthropicMessage

            return isinstance(message, AnthropicMessage)
        except ImportError:
            return False

    @staticmethod
    def can_normalize_chunk(chunk: Any) -> bool:
        try:
            from anthropic.types import MessageStreamEvent

            return isinstance(chunk, MessageStreamEvent)
        except ImportError:
            return False


class GoogleNormalizer(BaseMessageNormalizer):
    @staticmethod
    def normalize(message: "GenerateContentResponse") -> ChatMessage:
        return ChatMessage(content=message.text, role="assistant")

    @staticmethod
    def normalize_chunk(chunk: "GenerateContentResponse") -> ChatMessageChunk:
        return ChatMessageChunk(content=chunk.text, role="assistant")

    @staticmethod
    def can_normalize(message: Any) -> bool:
        try:
            from google.generativeai.types.generation_types import (  # pyright: ignore[reportMissingTypeStubs]
                GenerateContentResponse,
            )

            return isinstance(message, GenerateContentResponse)
        except ImportError:
            return False

    @staticmethod
    def can_normalize_chunk(chunk: Any) -> bool:
        return GoogleNormalizer.can_normalize(chunk)


class OllamaNormalizer(BaseMessageNormalizer):
    @staticmethod
    def normalize(message: dict[str, Any]) -> ChatMessage:
        msg = message["message"]
        return ChatMessage(content=msg["content"], role=msg["role"])

    @staticmethod
    def normalize_chunk(chunk: dict[str, Any]) -> ChatMessageChunk:
        msg = chunk["message"]
        return ChatMessageChunk(content=msg["content"], role=msg["role"])

    @staticmethod
    def can_normalize(message: Any) -> bool:
        if not isinstance(message, dict):
            return False
        if "message" not in message:
            return False
        return DictNormalizer.can_normalize(message["message"])

    @staticmethod
    def can_normalize_chunk(chunk: Any) -> bool:
        return OllamaNormalizer.can_normalize(chunk)


class NormalizerRegistry:
    def __init__(self) -> None:
        self._strategies: dict[str, type[BaseMessageNormalizer]] = {
            "google": GoogleNormalizer,
            "anthropic": AnthropicNormalizer,
            "openai": OpenAINormalizer,
            "ollama": OllamaNormalizer,
            "dict": DictNormalizer,
            "string": StringNormalizer,
        }

    # TODO: throw error if provider already exists and a way to force overwrite
    def register(self, provider: str, strategy: type[BaseMessageNormalizer]) -> None:
        self._strategies[provider] = strategy


registry = NormalizerRegistry()


def normalize_message(message: Any) -> ChatMessage:
    for strategy in registry._strategies.values():
        if strategy.can_normalize(message):
            return strategy.normalize(message)
    raise ValueError(
        f"Could not find a normalizer for message of type {type(message)}: {message}"
        "Consider registering a custom normalizer"
    )


def normalize_message_chunk(chunk: Any) -> ChatMessageChunk:
    for strategy in registry._strategies.values():
        if strategy.can_normalize_chunk(chunk):
            return strategy.normalize_chunk(chunk)
    raise ValueError(
        f"Could not find a normalizer for message chunk of type {type(chunk)}: {chunk}"
        "Consider registering a custom normalizer"
    )
