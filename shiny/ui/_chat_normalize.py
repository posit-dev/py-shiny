import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional, cast

from htmltools import HTML, Tagifiable

from ._chat_types import ChatMessage

if TYPE_CHECKING:
    from anthropic.types import Message as AnthropicMessage
    from anthropic.types import MessageStreamEvent

    if sys.version_info >= (3, 9):
        from google.generativeai.types.generation_types import (  # pyright: ignore[reportMissingTypeStubs]
            GenerateContentResponse,
        )
    else:

        class GenerateContentResponse:
            text: str

    from langchain_core.messages import BaseMessage, BaseMessageChunk
    from openai.types.chat import ChatCompletion, ChatCompletionChunk


class BaseMessageNormalizer(ABC):
    @abstractmethod
    def normalize(self, message: Any) -> ChatMessage:
        pass

    @abstractmethod
    def normalize_chunk(self, chunk: Any) -> ChatMessage:
        pass

    @abstractmethod
    def can_normalize(self, message: Any) -> bool:
        pass

    @abstractmethod
    def can_normalize_chunk(self, chunk: Any) -> bool:
        pass


class StringNormalizer(BaseMessageNormalizer):
    def normalize(self, message: Any) -> ChatMessage:
        x = cast(Optional[str], message)
        return ChatMessage(content=x or "", role="assistant")

    def normalize_chunk(self, chunk: Any) -> ChatMessage:
        x = cast(Optional[str], chunk)
        return ChatMessage(content=x or "", role="assistant")

    def can_normalize(self, message: Any) -> bool:
        return isinstance(message, (str, HTML)) or message is None

    def can_normalize_chunk(self, chunk: Any) -> bool:
        return isinstance(chunk, (str, HTML)) or chunk is None


class DictNormalizer(BaseMessageNormalizer):
    def normalize(self, message: Any) -> ChatMessage:
        x = cast("dict[str, Any]", message)
        if "content" not in x:
            raise ValueError("Message must have 'content' key")
        return ChatMessage(content=x["content"], role=x.get("role", "assistant"))

    def normalize_chunk(self, chunk: Any) -> ChatMessage:
        x = cast("dict[str, Any]", chunk)
        if "content" not in x:
            raise ValueError("Message must have 'content' key")
        return ChatMessage(content=x["content"], role=x.get("role", "assistant"))

    def can_normalize(self, message: Any) -> bool:
        return isinstance(message, dict)

    def can_normalize_chunk(self, chunk: Any) -> bool:
        return isinstance(chunk, dict)


class TagifiableNormalizer(DictNormalizer):
    def normalize(self, message: Any) -> ChatMessage:
        x = cast("Tagifiable", message)
        return super().normalize({"content": x})

    def normalize_chunk(self, chunk: Any) -> ChatMessage:
        x = cast("Tagifiable", chunk)
        return super().normalize_chunk({"content": x})

    def can_normalize(self, message: Any) -> bool:
        return isinstance(message, Tagifiable)

    def can_normalize_chunk(self, chunk: Any) -> bool:
        return isinstance(chunk, Tagifiable)


class LangChainNormalizer(BaseMessageNormalizer):
    def normalize(self, message: Any) -> ChatMessage:
        x = cast("BaseMessage", message)
        if isinstance(x.content, list):  # type: ignore
            raise ValueError(
                "The `message.content` provided seems to represent numerous messages. "
                "Consider iterating over `message.content` and calling .append_message() on each iteration."
            )
        return ChatMessage(content=x.content, role="assistant")

    def normalize_chunk(self, chunk: Any) -> ChatMessage:
        x = cast("BaseMessageChunk", chunk)
        if isinstance(x.content, list):  # type: ignore
            raise ValueError(
                "The `message.content` provided seems to represent numerous messages. "
                "Consider iterating over `message.content` and calling .append_message() on each iteration."
            )
        return ChatMessage(content=x.content, role="assistant")

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
    def normalize(self, message: Any) -> ChatMessage:
        x = cast("ChatCompletion", message)
        return super().normalize(x.choices[0].message.content)

    def normalize_chunk(self, chunk: Any) -> ChatMessage:
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
    def normalize(self, message: Any) -> ChatMessage:
        x = cast("AnthropicMessage", message)
        content = x.content[0]
        if content.type != "text":
            raise ValueError(
                f"Anthropic message type {content.type} not supported. "
                "Only 'text' type is currently supported"
            )
        return ChatMessage(content=content.text, role="assistant")

    def normalize_chunk(self, chunk: Any) -> ChatMessage:
        x = cast("MessageStreamEvent", chunk)
        content = ""
        if x.type == "content_block_delta":
            if x.delta.type != "text_delta":
                raise ValueError(
                    f"Anthropic message delta type {x.delta.type} not supported. "
                    "Only 'text_delta' type is supported"
                )
            content = x.delta.text

        return ChatMessage(content=content, role="assistant")

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
            return (
                isinstance(chunk, RawContentBlockDeltaEvent)
                or isinstance(chunk, RawContentBlockStartEvent)
                or isinstance(chunk, RawContentBlockStopEvent)
                or isinstance(chunk, RawMessageDeltaEvent)
                or isinstance(chunk, RawMessageStartEvent)
                or isinstance(chunk, RawMessageStopEvent)
            )
        except Exception:
            return False


class GoogleNormalizer(BaseMessageNormalizer):
    def normalize(self, message: Any) -> ChatMessage:
        x = cast("GenerateContentResponse", message)
        return ChatMessage(content=x.text, role="assistant")

    def normalize_chunk(self, chunk: Any) -> ChatMessage:
        x = cast("GenerateContentResponse", chunk)
        return ChatMessage(content=x.text, role="assistant")

    def can_normalize(self, message: Any) -> bool:
        try:
            import google.generativeai.types.generation_types as gtypes  # pyright: ignore[reportMissingTypeStubs, reportMissingImports]

            return isinstance(
                message,
                gtypes.GenerateContentResponse,  # pyright: ignore[reportUnknownMemberType]
            )
        except Exception:
            return False

    def can_normalize_chunk(self, chunk: Any) -> bool:
        return self.can_normalize(chunk)


class OllamaNormalizer(DictNormalizer):
    def normalize(self, message: Any) -> ChatMessage:
        x = cast("dict[str, Any]", message["message"])
        return super().normalize(x)

    def normalize_chunk(self, chunk: "dict[str, Any]") -> ChatMessage:
        msg = cast("dict[str, Any]", chunk["message"])
        return super().normalize_chunk(msg)

    def can_normalize(self, message: Any) -> bool:
        try:
            from ollama import ChatResponse

            # Ollama<0.4 used TypedDict (now it uses pydantic)
            # https://github.com/ollama/ollama-python/pull/276
            if isinstance(ChatResponse, dict):
                return "message" in message and super().can_normalize(
                    message["message"]
                )
            else:
                return isinstance(message, ChatResponse)
        except Exception:
            return False

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
            "tagify": TagifiableNormalizer(),
            "dict": DictNormalizer(),
            "string": StringNormalizer(),
        }

    def register(
        self, provider: str, strategy: BaseMessageNormalizer, force: bool = False
    ) -> None:
        if provider in self._strategies:
            if force:
                del self._strategies[provider]
            else:
                raise ValueError(f"Provider {provider} already exists in registry")
        # Update the strategies dict such that the new strategy is the first to be considered
        self._strategies = {provider: strategy, **self._strategies}


message_normalizer_registry = NormalizerRegistry()


def register_custom_normalizer(
    provider: str, normalizer: BaseMessageNormalizer, force: bool = False
) -> None:
    """
    Register a custom normalizer for handling specific message types.

    Parameters
    ----------
    provider : str
        A unique identifier for this normalizer in the registry
    normalizer : BaseMessageNormalizer
        A normalizer instance that can handle your specific message type
    force : bool, optional
        Whether to override an existing normalizer with the same provider name,
        by default False

    Examples
    --------
    >>> class MyCustomMessage:
    ...     def __init__(self, content):
    ...         self.content = content
    ...
    >>> class MyCustomNormalizer(StringNormalizer):
    ...     def normalize(self, message):
    ...         return ChatMessage(content=message.content, role="assistant")
    ...     def can_normalize(self, message):
    ...         return isinstance(message, MyCustomMessage)
    ...
    >>> register_custom_normalizer("my_provider", MyCustomNormalizer())
    """
    message_normalizer_registry.register(provider, normalizer, force)


def normalize_message(message: Any) -> ChatMessage:
    strategies = message_normalizer_registry._strategies
    for strategy in strategies.values():
        if strategy.can_normalize(message):
            return strategy.normalize(message)
    raise ValueError(
        f"Could not find a normalizer for message of type {type(message)}: {message}. "
        "Consider registering a custom normalizer via shiny.ui._chat_types.registry.register()"
    )


def normalize_message_chunk(chunk: Any) -> ChatMessage:
    strategies = message_normalizer_registry._strategies
    for strategy in strategies.values():
        if strategy.can_normalize_chunk(chunk):
            return strategy.normalize_chunk(chunk)
    raise ValueError(
        f"Could not find a normalizer for message chunk of type {type(chunk)}: {chunk}. "
        "Consider registering a custom normalizer via shiny.ui._chat_normalize.register_custom_normalizer()"
    )
