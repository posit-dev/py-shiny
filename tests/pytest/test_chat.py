from __future__ import annotations

import sys
from datetime import datetime

from shiny.ui._chat_normalize import normalize_message, normalize_message_chunk

# TODO:
# 1. Feed these messages into an actual Chat() instance.
# 2. Provide multiple chunks and ensure chat.get_messages() accumulates them correctly.


def test_string_normalization():
    msg = normalize_message_chunk("Hello world!")
    assert msg == {"content": "Hello world!", "role": "assistant"}


def test_dict_normalization():
    msg = normalize_message_chunk({"content": "Hello world!", "role": "assistant"})
    assert msg == {"content": "Hello world!", "role": "assistant"}


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
    assert normalize_message(msg) == {"content": "Hello world!", "role": "assistant"}

    # Mock & normalize return value of BaseChatModel.stream()
    chunk = BaseMessageChunk(content="Hello ", type="foo")
    assert normalize_message_chunk(chunk) == {"content": "Hello ", "role": "assistant"}


def test_google_normalization():
    # Not available for Python 3.8
    if sys.version_info < (3, 9):
        return

    from google.generativeai import (  # pyright: ignore[reportMissingTypeStubs]
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

    assert normalize_message(msg) == {"content": "Hello world!", "role": "assistant"}

    # Mock return object from Anthropic().messages.create(stream=True)
    chunk = RawContentBlockDeltaEvent(
        delta=TextDelta(type="text_delta", text="Hello "),
        type="content_block_delta",
        index=0,
    )

    assert normalize_message_chunk(chunk) == {"content": "Hello ", "role": "assistant"}


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

    msg = normalize_message(completion)
    assert msg == {"content": "Hello world!", "role": "assistant"}

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

    msg = normalize_message_chunk(chunk)
    assert msg == {"content": "Hello ", "role": "assistant"}
