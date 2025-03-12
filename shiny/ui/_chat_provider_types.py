import sys
from typing import TYPE_CHECKING, Literal, Union

from ._chat_types import ChatMessageDict

if TYPE_CHECKING:
    from anthropic.types import MessageParam as AnthropicMessage
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
    from ollama import Message as OllamaMessage
    from openai.types.chat import (
        ChatCompletionAssistantMessageParam,
        ChatCompletionSystemMessageParam,
        ChatCompletionUserMessageParam,
    )

    if sys.version_info >= (3, 9):
        import google.generativeai.types as gtypes  # pyright: ignore[reportMissingTypeStubs]

        GoogleMessage = gtypes.ContentDict
    else:
        GoogleMessage = object

    LangChainMessage = Union[AIMessage, HumanMessage, SystemMessage]
    OpenAIMessage = Union[
        ChatCompletionAssistantMessageParam,
        ChatCompletionSystemMessageParam,
        ChatCompletionUserMessageParam,
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
    message: ChatMessageDict, format: ProviderMessageFormat
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


def as_anthropic_message(message: ChatMessageDict) -> "AnthropicMessage":
    from anthropic.types import MessageParam as AnthropicMessage

    if message["role"] == "system":
        raise ValueError(
            "Anthropic requires a system prompt to be specified in the `.create()` method"
        )
    return AnthropicMessage(content=message["content"], role=message["role"])


def as_google_message(message: ChatMessageDict) -> "GoogleMessage":
    if sys.version_info < (3, 9):
        raise ValueError("Google requires Python 3.9")

    import google.generativeai.types as gtypes  # pyright: ignore[reportMissingTypeStubs]

    role = message["role"]

    if role == "system":
        raise ValueError(
            "Google requires a system prompt to be specified in the `GenerativeModel()` constructor."
        )
    elif role == "assistant":
        role = "model"
    return gtypes.ContentDict(parts=[message["content"]], role=role)


def as_langchain_message(message: ChatMessageDict) -> "LangChainMessage":
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    content = message["content"]
    role = message["role"]
    if role == "system":
        return SystemMessage(content=content)
    if role == "assistant":
        return AIMessage(content=content)
    if role == "user":
        return HumanMessage(content=content)
    raise ValueError(f"Unknown role: {message['role']}")


def as_openai_message(message: ChatMessageDict) -> "OpenAIMessage":
    from openai.types.chat import (
        ChatCompletionAssistantMessageParam,
        ChatCompletionSystemMessageParam,
        ChatCompletionUserMessageParam,
    )

    content = message["content"]
    role = message["role"]
    if role == "system":
        return ChatCompletionSystemMessageParam(content=content, role=role)
    if role == "assistant":
        return ChatCompletionAssistantMessageParam(content=content, role=role)
    if role == "user":
        return ChatCompletionUserMessageParam(content=content, role=role)
    raise ValueError(f"Unknown role: {role}")


def as_ollama_message(message: ChatMessageDict) -> "OllamaMessage":
    from ollama import Message as OllamaMessage

    return OllamaMessage(content=message["content"], role=message["role"])
