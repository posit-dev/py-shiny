import json
import sys
from typing import TYPE_CHECKING, Literal, Union

from . import _chat_types as ct

if TYPE_CHECKING:
    from anthropic.types import MessageParam as AnthropicMessage
    from langchain_core.messages import (
        AIMessage,
        HumanMessage,
        SystemMessage,
        ToolMessage,
    )
    from ollama import Message as OllamaMessage
    from openai.types.chat import (
        ChatCompletionAssistantMessageParam,
        ChatCompletionSystemMessageParam,
        ChatCompletionToolMessageParam,
        ChatCompletionUserMessageParam,
    )

    if sys.version_info >= (3, 9):
        import google.generativeai.types as gtypes  # pyright: ignore[reportMissingTypeStubs]

        GoogleMessage = gtypes.ContentDict
    else:
        GoogleMessage = object

    LangChainMessage = Union[AIMessage, HumanMessage, SystemMessage, ToolMessage]
    OpenAIMessage = Union[
        ChatCompletionAssistantMessageParam,
        ChatCompletionSystemMessageParam,
        ChatCompletionUserMessageParam,
        ChatCompletionToolMessageParam,
    ]

    ProviderMessage = Union[
        AnthropicMessage, GoogleMessage, LangChainMessage, OpenAIMessage, OllamaMessage
    ]
else:
    AnthropicMessage = GoogleMessage = LangChainMessage = OpenAIMessage = (
        OllamaMessage
    ) = ProviderMessage = object

ProviderMessageFormat = Literal[
    "anthropic",
    "google",
    "langchain",
    "openai",
    "ollama",
]


# TODO: use a strategy pattern to allow others to register
# their own message formats
def as_provider_message(
    message: ct.ChatMessage, format: ProviderMessageFormat
) -> "ProviderMessage":
    if format == "anthropic":
        return as_anthropic_message(message)
    if format == "google":
        return as_google_message(message)
    if format == "langchain":
        return as_langchain_message(message)
    if format == "openai":
        return as_openai_message(message)
    if format == "ollama":
        return as_ollama_message(message)
    raise ValueError(f"Unknown format: {format}")


def as_anthropic_message(message: ct.ChatMessage) -> "AnthropicMessage":
    from anthropic.types import MessageParam as AnthropicMessage
    from anthropic.types import TextBlockParam, ToolResultBlockParam, ToolUseBlockParam

    if isinstance(message, ct.SystemMessage):
        raise ValueError(
            "Anthropic requires a system prompt to be specified in the `.create()` method"
        )
    elif isinstance(message, ct.AssistantMessage):
        text = TextBlockParam(text=message.content, type="text")
        if message.tool_calls is None:
            return AnthropicMessage(role="assistant", content=[text])

        tools: list[ToolUseBlockParam] = []
        for tool_call in message.tool_calls:
            tool = ToolUseBlockParam(
                type="tool_use",
                id=tool_call["id"],
                name=tool_call["function"]["name"],
                # TODO: try/catch here?
                input=json.loads(tool_call["function"]["arguments"]),
            )
            tools.append(tool)

        return AnthropicMessage(
            role="assistant",
            content=[text, *tools],
        )

    elif isinstance(message, ct.ToolMessage):
        tool_result = ToolResultBlockParam(
            type="tool_result",
            tool_use_id=message.tool_call_id,
            content=str(json.loads(message.content)[message.name]),
        )
        return AnthropicMessage(role="user", content=[tool_result])
    elif isinstance(message, ct.UserMessage):
        text = TextBlockParam(text=message.content, type="text")
        return AnthropicMessage(role="user", content=[text])


def as_google_message(message: ct.ChatMessage) -> "GoogleMessage":
    if sys.version_info < (3, 9):
        raise ValueError("Google requires Python 3.9")

    import google.generativeai.types as gtypes  # pyright: ignore[reportMissingTypeStubs]

    role = message.role
    if isinstance(message, ct.SystemMessage):
        raise ValueError(
            "Google requires a system prompt to be specified in the `GenerativeModel()` constructor."
        )
    elif isinstance(message, ct.AssistantMessage):
        role = "model"
    elif isinstance(message, ct.ToolMessage):
        raise ValueError("TODO: implement tool messages")
    return gtypes.ContentDict(parts=[message.content], role=role)


def as_langchain_message(message: ct.ChatMessage) -> "LangChainMessage":
    from langchain_core.messages import (
        AIMessage,
        HumanMessage,
        SystemMessage,
        ToolMessage,
    )

    content = message.content
    if isinstance(message, ct.SystemMessage):
        return SystemMessage(content=content)
    if isinstance(message, ct.AssistantMessage):
        res = AIMessage(content=content)
        if message.tool_calls is None:
            return res

        from langchain_core.messages.tool import ToolCall

        tool_calls: list[ToolCall] = []
        for tool_call in message.tool_calls:
            x = ToolCall(
                id=tool_call["id"],
                name=tool_call["function"]["name"],
                # TODO: try/catch here?
                args=json.loads(tool_call["function"]["arguments"]),
            )
            tool_calls.append(x)

        res.tool_calls = tool_calls
        return res

    if isinstance(message, ct.UserMessage):
        return HumanMessage(content=content)
    if isinstance(message, ct.ToolMessage):
        return ToolMessage(
            tool_call_id=message.tool_call_id,
            type="tool",
            content=content,
        )
    raise ValueError(f"Unknown role: {message['role']}")


def as_openai_message(message: ct.ChatMessage) -> "OpenAIMessage":
    from openai.types.chat import (
        ChatCompletionAssistantMessageParam,
        ChatCompletionMessageToolCallParam,
        ChatCompletionSystemMessageParam,
        ChatCompletionToolMessageParam,
        ChatCompletionUserMessageParam,
    )

    content = message.content
    if isinstance(message, ct.SystemMessage):
        return ChatCompletionSystemMessageParam(content=content, role=message.role)
    if isinstance(message, ct.AssistantMessage):
        res = ChatCompletionAssistantMessageParam(content=content, role=message.role)
        if message.tool_calls is None:
            return res
        tool_calls: list[ChatCompletionMessageToolCallParam] = []
        for tool_call in message.tool_calls:
            x = ChatCompletionMessageToolCallParam(
                id=tool_call["id"],
                function=tool_call["function"],
                type="function",
            )
            tool_calls.append(x)
        res["tool_calls"] = tool_calls
        return res
    if isinstance(message, ct.UserMessage):
        return ChatCompletionUserMessageParam(content=content, role=message.role)
    if isinstance(message, ct.ToolMessage):
        return ChatCompletionToolMessageParam(
            content=content,
            role=message.role,
            tool_call_id=message.tool_call_id,
        )
    raise ValueError(f"Unknown role: {message.role}")


def as_ollama_message(message: ct.ChatMessage) -> "OllamaMessage":
    from ollama import Message as OllamaMessage

    return OllamaMessage(content=message.content, role=message.role)
