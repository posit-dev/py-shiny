from __future__ import annotations

import sys
from datetime import datetime
from typing import Union, cast, get_args, get_origin

import pytest

from shiny import Session
from shiny._namespaces import Root
from shiny.module import ResolvedId
from shiny.session import session_context
from shiny.types import MISSING
from shiny.ui import Chat
from shiny.ui._chat_normalize import normalize_message, normalize_message_chunk
from shiny.ui._chat_types import ChatMessage, ChatMessageDict, Role, TransformedMessage

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


class _MockSession:
    ns: ResolvedId = Root
    app: object = None
    id: str = "mock-session"

    def on_ended(self, callback: object) -> None:
        pass

    def _increment_busy_count(self) -> None:
        pass


test_session = cast(Session, _MockSession())


# Check if a type is part of a Union
def is_type_in_union(type: object, union: object) -> bool:
    if get_origin(union) is Union:
        return type in get_args(union)
    return False


def transformed_message(content: str, role: Role) -> TransformedMessage:
    return TransformedMessage.from_chat_message(ChatMessage(content=content, role=role))


def test_chat_message_trimming():
    with session_context(test_session):
        chat = Chat(id="chat")

        # Default tokenizer gives a token count
        def generate_content(token_count: int) -> str:
            n = int(token_count / 2)
            return " ".join(["foo" for _ in range(1, n)])

        msgs = (
            transformed_message(
                content=generate_content(102),
                role="system",
            ),
        )

        # Throws since system message is too long
        with pytest.raises(ValueError):
            chat._trim_messages(msgs, token_limits=(100, 0), format=MISSING)

        msgs = (
            transformed_message(content=generate_content(100), role="system"),
            transformed_message(content=generate_content(2), role="user"),
        )

        # Throws since only the system message fits
        with pytest.raises(ValueError):
            chat._trim_messages(msgs, token_limits=(100, 0), format=MISSING)

        # Raising the limit should allow both messages to fit
        trimmed = chat._trim_messages(msgs, token_limits=(103, 0), format=MISSING)
        assert len(trimmed) == 2

        content1 = generate_content(100)
        content2 = generate_content(10)
        content3 = generate_content(2)

        msgs = (
            transformed_message(
                content=content1,
                role="system",
            ),
            transformed_message(
                content=content2,
                role="user",
            ),
            transformed_message(
                content=content3,
                role="user",
            ),
        )

        # Should discard the 1st user message
        trimmed = chat._trim_messages(msgs, token_limits=(103, 0), format=MISSING)
        assert len(trimmed) == 2
        contents = [msg.content_server for msg in trimmed]
        assert contents == [content1, content3]

        content1 = generate_content(50)
        content2 = generate_content(10)
        content3 = generate_content(50)
        content4 = generate_content(2)

        msgs = (
            transformed_message(
                content=content1,
                role="system",
            ),
            transformed_message(
                content=content2,
                role="user",
            ),
            transformed_message(
                content=content3,
                role="system",
            ),
            transformed_message(
                content=content4,
                role="user",
            ),
        )

        # Should discard the 1st user message
        trimmed = chat._trim_messages(msgs, token_limits=(103, 0), format=MISSING)
        assert len(trimmed) == 3
        contents = [msg.content_server for msg in trimmed]
        assert contents == [content1, content3, content4]

        content1 = generate_content(50)
        content2 = generate_content(10)

        msgs = (
            transformed_message(
                content=content1,
                role="assistant",
            ),
            transformed_message(
                content=content2,
                role="user",
            ),
        )

        # Anthropic requires 1st message to be a user message
        trimmed = chat._trim_messages(msgs, token_limits=(30, 0), format="anthropic")
        assert len(trimmed) == 1
        contents = [msg.content_server for msg in trimmed]
        assert contents == [content2]


# ------------------------------------------------------------------------------------
# Unit tests for normalize_message() and normalize_message_chunk().
#
# This is where we go from provider's response object to ChatMessage.
#
# The general idea is to check that the provider's output message type match our
# expectations. If these tests fail, it doesn't not necessarily mean that our code is
# wrong (i.e., updating the test may be sufficient), but we'll still want to be aware
# and double-check our code.
# ------------------------------------------------------------------------------------


def test_string_normalization():
    m = normalize_message_chunk("Hello world!")
    assert m.content == "Hello world!"
    assert m.role == "assistant"


def test_dict_normalization():
    m = normalize_message_chunk({"content": "Hello world!", "role": "assistant"})
    assert m.content == "Hello world!"
    assert m.role == "assistant"


def test_langchain_normalization():
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import BaseMessage, BaseMessageChunk

    # Make sure return type of the .invoke()/.stream() methods haven't changed
    # (If they do, we may need to update the mock and normalization functions)
    assert BaseChatModel.invoke.__annotations__["return"] == "BaseMessage"
    assert (
        BaseChatModel.stream.__annotations__["return"] == "Iterator[BaseMessageChunk]"
    )

    # Mock & normalize return value of BaseChatModel.invoke()
    msg = BaseMessage(content="Hello world!", role="assistant", type="foo")
    m = normalize_message(msg)
    assert m.content == "Hello world!"
    assert m.role == "assistant"

    # Mock & normalize return value of BaseChatModel.stream()
    chunk = BaseMessageChunk(content="Hello ", type="foo")
    m = normalize_message_chunk(chunk)
    assert m.content == "Hello "
    assert m.role == "assistant"


def test_google_normalization():
    # Not available for Python 3.8
    if sys.version_info < (3, 9):
        return

    from google.generativeai.generative_models import (  # pyright: ignore[reportMissingTypeStubs]
        GenerativeModel,
    )

    generate_content = GenerativeModel.generate_content  # type: ignore

    assert (
        generate_content.__annotations__["return"]
        == "generation_types.GenerateContentResponse"
    )

    # Not worth mocking the return value of generate_content() since it's a complex object
    # and fairly simple to normalize....


def test_anthropic_normalization():
    from anthropic import Anthropic, AsyncAnthropic
    from anthropic.resources.messages import AsyncMessages, Messages
    from anthropic.types import TextBlock, Usage
    from anthropic.types.message import Message
    from anthropic.types.raw_content_block_delta_event import RawContentBlockDeltaEvent
    from anthropic.types.text_delta import TextDelta

    # Make sure return type of Anthropic().messages.create() hasn't changed
    assert isinstance(Anthropic().messages, Messages)
    assert isinstance(AsyncAnthropic().messages, AsyncMessages)

    # Make sure return type of llm.messages.create() hasn't changed
    assert (
        AsyncMessages.create.__annotations__["return"]
        == "Message | AsyncStream[RawMessageStreamEvent]"
    )
    assert (
        Messages.create.__annotations__["return"]
        == "Message | Stream[RawMessageStreamEvent]"
    )

    # Mock return object from Anthropic().messages.create()
    msg = Message(
        content=[
            TextBlock(type="text", text="Hello world!"),
        ],
        role="assistant",
        id="foo",
        type="message",
        model="foo",
        usage=Usage(input_tokens=0, output_tokens=0),
    )

    m = normalize_message(msg)
    assert m.content == "Hello world!"
    assert m.role == "assistant"

    # Mock return object from Anthropic().messages.create(stream=True)
    chunk = RawContentBlockDeltaEvent(
        delta=TextDelta(type="text_delta", text="Hello "),
        type="content_block_delta",
        index=0,
    )

    m = normalize_message_chunk(chunk)
    assert m.content == "Hello "
    assert m.role == "assistant"


def test_openai_normalization():
    import openai.types.chat.chat_completion as cc
    import openai.types.chat.chat_completion_chunk as ccc
    from openai import AsyncOpenAI, OpenAI
    from openai.resources.chat.completions import AsyncCompletions, Completions
    from openai.types.chat import (
        ChatCompletion,
        ChatCompletionChunk,
        ChatCompletionMessage,
    )

    # Make sure return type of OpenAI().chat.completions hasn't changed
    assert isinstance(OpenAI(api_key="fake").chat.completions, Completions)
    assert isinstance(AsyncOpenAI(api_key="fake").chat.completions, AsyncCompletions)

    assert (
        Completions.create.__annotations__["return"]
        == "ChatCompletion | Stream[ChatCompletionChunk]"
    )
    assert (
        AsyncCompletions.create.__annotations__["return"]
        == "ChatCompletion | AsyncStream[ChatCompletionChunk]"
    )

    # Mock return object from OpenAI().chat.completions.create()
    completion = ChatCompletion(
        id="foo",
        model="gpt-4",
        object="chat.completion",
        choices=[
            cc.Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="Hello world!",
                    role="assistant",
                ),
            )
        ],
        created=int(datetime.now().timestamp()),
    )

    m = normalize_message(completion)
    assert m.content == "Hello world!"
    assert m.role == "assistant"

    # Mock return object from OpenAI().chat.completions.create(stream=True)
    chunk = ChatCompletionChunk(
        id="foo",
        object="chat.completion.chunk",
        model="gpt-4o",
        created=int(datetime.now().timestamp()),
        choices=[
            ccc.Choice(
                index=0,
                delta=ccc.ChoiceDelta(
                    content="Hello ",
                    role="assistant",
                ),
            )
        ],
    )

    m = normalize_message_chunk(chunk)
    assert m.content == "Hello "
    assert m.role == "assistant"


def test_ollama_normalization():
    from ollama import ChatResponse
    from ollama import Message as OllamaMessage

    # Mock return object from ollama.chat()
    msg = ChatResponse(
        message=OllamaMessage(content="Hello world!", role="assistant"),
    )

    msg_dict = {"content": "Hello world!", "role": "assistant"}
    m = normalize_message(msg)
    assert m.content == msg_dict["content"]
    assert m.role == msg_dict["role"]

    m = normalize_message_chunk(msg)
    assert m.content == msg_dict["content"]
    assert m.role == msg_dict["role"]


# ------------------------------------------------------------------------------------
# Unit tests for as_provider_message()
#
# This is where we go from our ChatMessage to a provider's message object
#
# The general idea is to check that the provider's input message type match our
# expectations. If these tests fail, it doesn't not necessarily mean that our code is
# wrong (i.e., updating the test may be sufficient), but we'll still want to be aware
# and double-check our code.
# ------------------------------------------------------------------------------------


def test_as_anthropic_message():
    from anthropic.resources.messages import AsyncMessages, Messages
    from anthropic.types import MessageParam

    from shiny.ui._chat_provider_types import as_anthropic_message

    # Make sure return type of llm.messages.create() hasn't changed
    assert AsyncMessages.create.__annotations__["messages"] == "Iterable[MessageParam]"
    assert Messages.create.__annotations__["messages"] == "Iterable[MessageParam]"

    msg = ChatMessageDict(content="I have a question", role="user")
    assert as_anthropic_message(msg) == MessageParam(
        content="I have a question", role="user"
    )


def test_as_google_message():
    from shiny.ui._chat_provider_types import as_google_message

    # Not available for Python 3.8
    if sys.version_info < (3, 9):
        return

    from google.generativeai.generative_models import (  # pyright: ignore[reportMissingTypeStubs]
        GenerativeModel,
    )

    generate_content = GenerativeModel.generate_content  # type: ignore

    assert generate_content.__annotations__["contents"] == "content_types.ContentsType"

    from google.generativeai.types import (  # pyright: ignore[reportMissingTypeStubs]
        content_types,
    )

    assert is_type_in_union(content_types.ContentDict, content_types.ContentsType)

    msg = ChatMessageDict(content="I have a question", role="user")
    assert as_google_message(msg) == content_types.ContentDict(
        parts=["I have a question"], role="user"
    )


def test_as_langchain_message():
    from langchain_core.language_models.base import (
        LanguageModelInput,
    )
    from langchain_core.language_models.base import (
        Sequence as LangchainSequence,  # pyright: ignore[reportPrivateImportUsage]
    )
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import (
        AIMessage,
        BaseMessage,
        HumanMessage,
        MessageLikeRepresentation,
        SystemMessage,
    )

    from shiny.ui._chat_provider_types import as_langchain_message

    assert BaseChatModel.invoke.__annotations__["input"] == "LanguageModelInput"
    assert BaseChatModel.stream.__annotations__["input"] == "LanguageModelInput"

    assert is_type_in_union(
        # Use `LangchainSequence` instead of `Sequence` to avoid incorrect comparison
        # between `typing.Sequence` and `collections.abc.Sequence`
        LangchainSequence[MessageLikeRepresentation],
        LanguageModelInput,
    )
    assert is_type_in_union(BaseMessage, MessageLikeRepresentation)

    assert issubclass(AIMessage, BaseMessage)
    assert issubclass(HumanMessage, BaseMessage)
    assert issubclass(SystemMessage, BaseMessage)

    msg = ChatMessageDict(content="I have a question", role="user")
    assert as_langchain_message(msg) == HumanMessage(content="I have a question")


def test_as_openai_message():
    from openai.resources.chat.completions import AsyncCompletions, Completions
    from openai.types.chat import (
        ChatCompletionAssistantMessageParam,
        ChatCompletionMessageParam,
        ChatCompletionSystemMessageParam,
        ChatCompletionUserMessageParam,
    )

    from shiny.ui._chat_provider_types import as_openai_message

    assert (
        Completions.create.__annotations__["messages"]
        == "Iterable[ChatCompletionMessageParam]"
    )

    assert (
        AsyncCompletions.create.__annotations__["messages"]
        == "Iterable[ChatCompletionMessageParam]"
    )

    assert is_type_in_union(
        ChatCompletionAssistantMessageParam, ChatCompletionMessageParam
    )
    assert is_type_in_union(
        ChatCompletionSystemMessageParam, ChatCompletionMessageParam
    )
    assert is_type_in_union(ChatCompletionUserMessageParam, ChatCompletionMessageParam)

    msg = ChatMessageDict(content="I have a question", role="user")
    assert as_openai_message(msg) == ChatCompletionUserMessageParam(
        content="I have a question", role="user"
    )


def test_as_ollama_message():
    import ollama
    from ollama import Message as OllamaMessage

    # ollama 0.4.2 added Callable to the type hints, but pyright complains about
    # missing arguments to the Callable type. We'll ignore this for now.
    # https://github.com/ollama/ollama-python/commit/b50a65b
    chat = ollama.chat  # type: ignore

    assert "ollama._types.Message" in str(chat.__annotations__["messages"])

    from shiny.ui._chat_provider_types import as_ollama_message

    msg = ChatMessageDict(content="I have a question", role="user")
    assert as_ollama_message(msg) == OllamaMessage(
        content="I have a question", role="user"
    )
