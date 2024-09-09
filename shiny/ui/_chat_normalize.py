import sys
import warnings
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional, cast

from ..types import TypedDict
from ._chat_types import (
    AssistantMessage,
    ChatMessage,
    ToolFunctionCall,
    ToolFunctionCallDelta,
)

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
    from litellm.types.utils import (  # pyright: ignore[reportMissingTypeStubs]
        ModelResponse,
    )
    from openai.types.chat import ChatCompletion, ChatCompletionChunk

    # https://python.langchain.com/v0.1/docs/modules/model_io/chat/function_calling/#response-streaming
    class LangChainToolCallChunk(TypedDict):
        name: str | None
        args: str
        id: str | None
        index: int


class BaseMessageNormalizer(ABC):
    @abstractmethod
    def normalize(self, message: Any) -> ChatMessage:
        pass

    @abstractmethod
    def normalize_chunk(
        self, chunk: Any
    ) -> tuple[AssistantMessage, Optional[ToolFunctionCall | ToolFunctionCallDelta]]:
        pass

    @abstractmethod
    def can_normalize(self, message: Any) -> bool:
        pass

    @abstractmethod
    def can_normalize_chunk(self, chunk: Any) -> bool:
        pass


class StringNormalizer(BaseMessageNormalizer):
    def normalize(self, message: Any):
        x = cast(Optional[str], message)
        return AssistantMessage(content=x or "")

    def normalize_chunk(
        self, chunk: Any
    ) -> tuple[AssistantMessage, Optional[ToolFunctionCall | ToolFunctionCallDelta]]:
        x = cast(Optional[str], chunk)
        return AssistantMessage(content=x or ""), None

    def can_normalize(self, message: Any):
        return isinstance(message, str) or message is None

    def can_normalize_chunk(self, chunk: Any):
        return isinstance(chunk, str) or chunk is None


class DictNormalizer(BaseMessageNormalizer):
    def normalize(self, message: Any):
        x = cast("dict[str, Any]", message)
        if "content" not in x:
            raise ValueError("Message must have 'content' key")
        return AssistantMessage(content=x["content"], role=x.get("role", "assistant"))

    def normalize_chunk(self, chunk: Any):
        x = cast("dict[str, Any]", chunk)
        if "content" not in x:
            raise ValueError("Message must have 'content' key")
        return (
            AssistantMessage(content=x["content"], role=x.get("role", "assistant")),
            None,
        )

    def can_normalize(self, message: Any):
        return isinstance(message, dict)

    def can_normalize_chunk(self, chunk: Any):
        return isinstance(chunk, dict)


class LangChainNormalizer(BaseMessageNormalizer):
    def normalize(self, message: Any):
        x = cast("BaseMessage", message)
        if isinstance(x.content, list):  # type: ignore
            raise ValueError(
                "The `message.content` provided seems to represent numerous messages. "
                "Consider iterating over `message.content` and calling .append_message() on each iteration."
            )
        if len(getattr(x, "tool_calls", [])) > 0:
            raise non_streaming_tool_error
        return AssistantMessage(content=x.content)

    def normalize_chunk(self, chunk: Any):
        x = cast("BaseMessageChunk", chunk)
        if isinstance(x.content, list):  # type: ignore
            raise ValueError(
                "The `message.content` provided seems to represent numerous messages. "
                "Consider iterating over `message.content` and calling .append_message() on each iteration."
            )

        msg = AssistantMessage(content=x.content)

        # It's on the ChatModel's subclass to implement tool calls, but from the
        # docs it appears to follow the same pattern as OpenAI
        # https://python.langchain.com/v0.1/docs/modules/model_io/chat/function_calling/#response-streaming
        tool_calls: list[LangChainToolCallChunk] = getattr(x, "tool_call_chunks", [])
        if len(tool_calls) == 0:
            return msg, None
        if len(tool_calls) > 1:
            warnings.warn(concurrent_tool_warning, stacklevel=2)
        tool_call = tool_calls[0]
        if tool_call["name"] is not None:
            tool_call = ToolFunctionCall(
                name=tool_call["name"],
                id=tool_call["id"],  # type: ignore
            )
        else:
            tool_call = ToolFunctionCallDelta(arguments=tool_call["args"])

        return msg, tool_call

    def can_normalize(self, message: Any):
        try:
            from langchain_core.messages import BaseMessage

            return isinstance(message, BaseMessage)
        except Exception:
            return False

    def can_normalize_chunk(self, chunk: Any):
        try:
            from langchain_core.messages import BaseMessageChunk

            return isinstance(chunk, BaseMessageChunk)
        except Exception:
            return False


class OpenAINormalizer(StringNormalizer):
    def normalize(self, message: Any):
        x = cast("ChatCompletion", message)
        msg = x.choices[0].message
        if msg.tool_calls is not None:
            raise non_streaming_tool_error
        return super().normalize(msg.content)

    def normalize_chunk(self, chunk: Any):
        x = cast("ChatCompletionChunk", chunk)
        d = x.choices[0].delta
        msg, _ = super().normalize_chunk(d.content)
        if d.tool_calls is None:
            return msg, None

        if len(d.tool_calls) > 1:
            warnings.warn(concurrent_tool_warning, stacklevel=2)

        tool_call = d.tool_calls[0]
        if tool_call.function is None:
            # CPS 2024-09-04: I don't think non-function tool calls are currently a thing,
            # but they might be in the future?
            raise ValueError(
                "`Chat()` currently only supports tool calls that are functions. "
                "Please report this issue to https://github.com/posit-dev/py-shiny"
            )

        # I'm pretty sure when the id is present, the name should also be.
        # And, when the id is not present, then arguments should be present.
        if tool_call.id is not None:
            func_call = ToolFunctionCall(
                id=tool_call.id,
                name=tool_call.function.name,  # type: ignore
            )
        else:
            func_call = ToolFunctionCallDelta(
                arguments=tool_call.function.arguments,  # type: ignore
                finished=x.choices[0].finish_reason == "tool_calls",
            )

        return msg, func_call

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


class LiteLlmNormalizer(OpenAINormalizer):
    def normalize(self, message: Any):
        x = cast("ModelResponse", message)
        return super().normalize(x)

    def normalize_chunk(self, chunk: Any):
        x = cast("ModelResponse", chunk)
        return super().normalize_chunk(x)

    def can_normalize(self, message: Any):
        try:
            from litellm.types.utils import (  # pyright: ignore[reportMissingTypeStubs]
                ModelResponse,
            )

            return isinstance(message, ModelResponse)
        except Exception:
            return False

    def can_normalize_chunk(self, chunk: Any):
        try:
            from litellm.types.utils import (  # pyright: ignore[reportMissingTypeStubs]
                ModelResponse,
            )

            return isinstance(chunk, ModelResponse)
        except Exception:
            return False


class AnthropicNormalizer(BaseMessageNormalizer):
    def normalize(self, message: Any):
        x = cast("AnthropicMessage", message)
        content = x.content[0]
        if content.type == "tool_use":
            raise non_streaming_tool_error
        if content.type != "text":
            raise ValueError(
                f"Anthropic message type {content.type} is currently not supported "
                "by `Chat()`"
            )
        return AssistantMessage(content=content.text)

    def normalize_chunk(self, chunk: Any):
        x = cast("MessageStreamEvent", chunk)
        if x.type == "content_block_delta" and x.delta.type == "text_delta":
            content = x.delta.text
        else:
            content = ""

        msg = AssistantMessage(content=content)

        tool_call = None
        if x.type == "content_block_start" and x.content_block.type == "tool_use":
            tool_call = ToolFunctionCall(
                id=x.content_block.id,
                name=x.content_block.name,
            )

        if x.type == "content_block_delta" and x.delta.type == "input_json_delta":
            tool_call = ToolFunctionCallDelta(arguments=x.delta.partial_json)

        if x.type == "message_delta" and x.delta.stop_reason == "tool_use":
            tool_call = ToolFunctionCallDelta(arguments="", finished=True)

        return msg, tool_call

    def can_normalize(self, message: Any):
        try:
            from anthropic.types import Message as AnthropicMessage

            return isinstance(message, AnthropicMessage)
        except Exception:
            return False

    def can_normalize_chunk(self, chunk: Any):
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
    def normalize(self, message: Any):
        x = cast("GenerateContentResponse", message)
        return AssistantMessage(content=x.text)

    def normalize_chunk(self, chunk: Any):
        x = cast("GenerateContentResponse", chunk)
        # TODO: implement tool call normalization
        return AssistantMessage(content=x.text), None

    def can_normalize(self, message: Any):
        try:
            import google.generativeai.types.generation_types as gtypes  # pyright: ignore[reportMissingTypeStubs, reportMissingImports]

            return isinstance(
                message,
                gtypes.GenerateContentResponse,  # pyright: ignore[reportUnknownMemberType]
            )
        except Exception:
            return False

    def can_normalize_chunk(self, chunk: Any):
        return self.can_normalize(chunk)


class OllamaNormalizer(DictNormalizer):
    def normalize(self, message: Any):
        x = cast("dict[str, Any]", message["message"])
        return super().normalize(x)

    def normalize_chunk(self, chunk: "dict[str, Any]"):
        msg = cast("dict[str, Any]", chunk["message"])
        # TODO: implement tool call normalization
        return super().normalize_chunk(msg)

    def can_normalize(self, message: Any):
        if not isinstance(message, dict):
            return False
        if "message" not in message:
            return False
        return super().can_normalize(message["message"])

    def can_normalize_chunk(self, chunk: Any):
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
            "litellm": LiteLlmNormalizer(),
            "ollama": OllamaNormalizer(),
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


def normalize_message(message: Any) -> ChatMessage:
    strategies = message_normalizer_registry._strategies
    for strategy in strategies.values():
        if strategy.can_normalize(message):
            return strategy.normalize(message)
    raise ValueError(
        f"Could not find a normalizer for message of type {type(message)}: {message}. "
        "Consider registering a custom normalizer via shiny.ui._chat_types.registry.register()"
    )


def normalize_message_chunk(
    chunk: Any,
) -> tuple[AssistantMessage, Optional[ToolFunctionCall | ToolFunctionCallDelta]]:
    strategies = message_normalizer_registry._strategies
    for strategy in strategies.values():
        if strategy.can_normalize_chunk(chunk):
            return strategy.normalize_chunk(chunk)
    raise ValueError(
        f"Could not find a normalizer for message chunk of type {type(chunk)}: {chunk}. "
        "Consider registering a custom normalizer via shiny.ui._chat_types.registry.register()"
    )


non_streaming_tool_error = ValueError(
    "`Chat()` currently only supports tool calls when streaming completions. "
    "Try setting `stream=True` when creating responses and "
    "`.append_message_stream()` to append the response to the chat."
)

concurrent_tool_warning = (
    "`Chat()` currently doesn't support multiple concurrent tool calls. "
    "Only the first tool call will be processed. "
    "Please report this issue to https://github.com/posit-dev/py-shiny"
)
