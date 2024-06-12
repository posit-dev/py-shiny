from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Literal, Optional, TypedDict, Union, cast

from typing_extensions import NotRequired

Role = Literal["assistant", "user", "system"]


class ChatMessage(TypedDict):
    content: str
    role: Role


# TODO: content should probably be [{"type": "text", "content": "..."}]
# in order to support multiple content types...
class UserMessage(TypedDict):
    content: str
    role: Literal["user"]
    original_content: str


class AssistantMessage(TypedDict):
    content: str
    role: Literal["assistant", "system"]
    content_type: Literal["markdown", "html"]
    # For chunked messages
    chunk_type: NotRequired[Literal["message_start", "message_end"]]


# A helper to supply defaults
def assistant_message(content: str) -> AssistantMessage:
    return {"content": content, "role": "assistant", "content_type": "markdown"}


if TYPE_CHECKING:
    from anthropic.types import Message as AnthropicMessage
    from anthropic.types import MessageStreamEvent
    from google.generativeai.types.generation_types import (  # pyright: ignore[reportMissingTypeStubs]
        GenerateContentResponse,
    )
    from langchain_core.messages import BaseMessage, BaseMessageChunk
    from openai.types.chat import ChatCompletion, ChatCompletionChunk


class BaseMessageNormalizer(ABC):
    @abstractmethod
    def normalize(self, message: Any) -> AssistantMessage:
        pass

    @abstractmethod
    def normalize_chunk(self, chunk: Any) -> AssistantMessage:
        pass

    @abstractmethod
    def can_normalize(self, message: Any) -> bool:
        pass

    @abstractmethod
    def can_normalize_chunk(self, chunk: Any) -> bool:
        pass


class StringNormalizer(BaseMessageNormalizer):
    def normalize(self, message: Any) -> AssistantMessage:
        x = cast(Optional[str], message)
        return assistant_message(content=x or "")

    def normalize_chunk(self, chunk: Any) -> AssistantMessage:
        return self.normalize(chunk)

    def can_normalize(self, message: Any) -> bool:
        return isinstance(message, str) or message is None

    def can_normalize_chunk(self, chunk: Any) -> bool:
        return self.can_normalize(chunk)


class DictNormalizer(BaseMessageNormalizer):
    def normalize(self, message: Any) -> AssistantMessage:
        x = cast(dict[str, Any], message)
        if "content" not in x:
            raise ValueError("Message must have 'content' key")
        if "role" in x and x["role"] not in ["assistant", "system"]:
            raise ValueError("Role must be 'assistant' or 'system'")
        return assistant_message(content=x["content"])

    def normalize_chunk(self, chunk: Any) -> AssistantMessage:
        res = self.normalize(chunk)
        if "chunk_type" in chunk:
            res["chunk_type"] = chunk["chunk_type"]
        return res

    def can_normalize(self, message: Any) -> bool:
        return isinstance(message, dict)

    def can_normalize_chunk(self, chunk: Any) -> bool:
        return self.can_normalize(chunk)


class LangChainNormalizer(BaseMessageNormalizer):
    def normalize(self, message: Any) -> AssistantMessage:
        x = cast("BaseMessage", message)
        if isinstance(x.content, list):  # type: ignore
            raise ValueError(
                "The `message.content` provided seems to represent numerous messages. "
                "Consider iterating over `message.content` and calling .append_message() on each iteration."
            )
        return assistant_message(content=x.content)

    def normalize_chunk(self, chunk: Any) -> AssistantMessage:
        x = cast("BaseMessageChunk", chunk)
        if isinstance(x.content, list):  # type: ignore
            raise ValueError(
                "The `message.content` provided seems to represent numerous messages. "
                "Consider iterating over `message.content` and calling .append_message() on each iteration."
            )
        return assistant_message(content=x.content)

    def can_normalize(self, message: Any) -> bool:
        try:
            from langchain_core.messages import BaseMessage

            return isinstance(message, BaseMessage)
        except Exception:
            return False

    def can_normalize_chunk(self, chunk: Any) -> bool:
        try:
            from langchain_core.messages import BaseMessageChunk

            return isinstance(chunk, BaseMessageChunk)
        except Exception:
            return False


class OpenAINormalizer(StringNormalizer):
    def normalize(self, message: Any) -> AssistantMessage:
        x = cast("ChatCompletion", message)
        return super().normalize(x.choices[0].message.content)

    def normalize_chunk(self, chunk: Any) -> AssistantMessage:
        x = cast("ChatCompletionChunk", chunk)
        return super().normalize_chunk(x.choices[0].delta.content)

    def can_normalize(self, message: Any) -> bool:
        try:
            from openai.types.chat import ChatCompletion

            return isinstance(message, ChatCompletion)
        except Exception:
            return False

    def can_normalize_chunk(self, chunk: Any) -> bool:
        try:
            from openai.types.chat import ChatCompletionChunk

            return isinstance(chunk, ChatCompletionChunk)
        except Exception:
            return False


class AnthropicNormalizer(BaseMessageNormalizer):
    def normalize(self, message: Any) -> AssistantMessage:
        x = cast("AnthropicMessage", message)
        content = x.content[0]
        if content.type != "text":
            raise ValueError(
                f"Anthropic message type {content.type} not supported. "
                "Only 'text' type is currently supported"
            )
        return assistant_message(content=content.text)

    def normalize_chunk(self, chunk: Any) -> AssistantMessage:
        x = cast("MessageStreamEvent", chunk)
        content = ""
        if x.type == "content_block_delta":
            if x.delta.type != "text_delta":
                raise ValueError(
                    f"Anthropic message delta type {x.delta.type} not supported. "
                    "Only 'text_delta' type is supported"
                )
            content = x.delta.text

        return assistant_message(content=content)

    def can_normalize(self, message: Any) -> bool:
        try:
            from anthropic.types import Message as AnthropicMessage

            return isinstance(message, AnthropicMessage)
        except Exception:
            return False

    def can_normalize_chunk(self, chunk: Any) -> bool:
        try:
            from anthropic.types import (
                RawContentBlockDeltaEvent,
                RawContentBlockStartEvent,
                RawContentBlockStopEvent,
                RawMessageDeltaEvent,
                RawMessageStartEvent,
                RawMessageStopEvent,
            )

            # The actual MessageStreamEvent is a generic, so isinstance() can't
            # be used to check the type. Instead, we manually construct the relevant
            # union of relevant classes...
            MessageStreamEvent = Union[
                RawMessageStartEvent,
                RawMessageDeltaEvent,
                RawMessageStopEvent,
                RawContentBlockStartEvent,
                RawContentBlockDeltaEvent,
                RawContentBlockStopEvent,
            ]

            return isinstance(chunk, MessageStreamEvent)
        except Exception:
            return False


class GoogleNormalizer(BaseMessageNormalizer):
    def normalize(self, message: Any) -> AssistantMessage:
        msg = cast("GenerateContentResponse", message)
        return assistant_message(content=msg.text)

    def normalize_chunk(self, chunk: Any) -> AssistantMessage:
        cnk = cast("GenerateContentResponse", chunk)
        return assistant_message(content=cnk.text)

    def can_normalize(self, message: Any) -> bool:
        try:
            from google.generativeai.types.generation_types import (  # pyright: ignore[reportMissingTypeStubs]
                GenerateContentResponse,
            )

            return isinstance(message, GenerateContentResponse)
        except Exception:
            return False

    def can_normalize_chunk(self, chunk: Any) -> bool:
        return self.can_normalize(chunk)


class OllamaNormalizer(DictNormalizer):
    def normalize(self, message: Any) -> AssistantMessage:
        x = cast(dict[str, Any], message["message"])
        return super().normalize(x)

    def normalize_chunk(self, chunk: dict[str, Any]) -> AssistantMessage:
        msg = cast(dict[str, Any], chunk["message"])
        return super().normalize_chunk(msg)

    def can_normalize(self, message: Any) -> bool:
        if not isinstance(message, dict):
            return False
        if "message" not in message:
            return False
        return super().can_normalize(message["message"])

    def can_normalize_chunk(self, chunk: Any) -> bool:
        return self.can_normalize(chunk)


class NormalizerRegistry:
    def __init__(self) -> None:
        # Order of strategies matters (the 1st one that can normalize the message is used)
        # So make sure to put the most specific strategies first
        self._strategies: dict[str, BaseMessageNormalizer] = {
            "openai": OpenAINormalizer(),
            "anthropic": AnthropicNormalizer(),
            "google": GoogleNormalizer(),
            "langchain": LangChainNormalizer(),
            "ollama": OllamaNormalizer(),
            "dict": DictNormalizer(),
            "string": StringNormalizer(),
        }

    def register(
        self, provider: str, strategy: BaseMessageNormalizer, force: bool = False
    ) -> None:
        if provider in self._strategies and not force:
            raise ValueError(f"Provider {provider} already exists in registry")
        # Update the strategies dict such that the new strategy is the first to be considered
        strategies = {provider: strategy}
        strategies.update(self._strategies)


message_normalizer_registry = NormalizerRegistry()


def normalize_message(message: Any) -> AssistantMessage:
    strategies = message_normalizer_registry._strategies
    for strategy in strategies.values():
        if strategy.can_normalize(message):
            return strategy.normalize(message)
    raise ValueError(
        f"Could not find a normalizer for message of type {type(message)}: {message}"
        "Consider registering a custom normalizer via shiny.ui._chat_types.registry.register()"
    )


def normalize_message_chunk(chunk: Any) -> AssistantMessage:
    strategies = message_normalizer_registry._strategies
    for strategy in strategies.values():
        if strategy.can_normalize_chunk(chunk):
            return strategy.normalize_chunk(chunk)
    raise ValueError(
        f"Could not find a normalizer for message chunk of type {type(chunk)}: {chunk}"
        "Consider registering a custom normalizer via shiny.ui._chat_types.registry.register()"
    )
