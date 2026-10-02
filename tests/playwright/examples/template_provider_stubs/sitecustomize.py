"""Stub LLM constructors before a template app starts in its child process.

Python imports sitecustomize from PYTHONPATH before running ``python -m shiny``.
This keeps the test's provider patches in the process that imports the app.
"""

import importlib
import importlib.util
import sys
import types

import pytest

from shiny.types import Jsonifiable


class DummyChatClient:
    def __init__(self, *args: object, **kwargs: object) -> None:
        pass

    async def stream_async(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("Template unexpectedly called an LLM provider")

    def stream(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("Template unexpectedly called an LLM provider")

    async def get_state(self) -> Jsonifiable:
        return {}

    async def set_state(self, value: Jsonifiable) -> None:
        pass


monkeypatch = pytest.MonkeyPatch()

if importlib.util.find_spec("langchain_openai") is None:
    stub = types.ModuleType("langchain_openai")
    stub.__dict__["ChatOpenAI"] = DummyChatClient
    monkeypatch.setitem(sys.modules, "langchain_openai", stub)
else:
    langchain_openai = importlib.import_module("langchain_openai")
    monkeypatch.setattr(langchain_openai, "ChatOpenAI", DummyChatClient)

if importlib.util.find_spec("chatlas") is not None:
    import chatlas

    for name in (
        "ChatOpenAI",
        "ChatAnthropic",
        "ChatGoogle",
        "ChatOllama",
        "ChatAzureOpenAI",
        "ChatBedrockAnthropic",
    ):
        if hasattr(chatlas, name):
            monkeypatch.setattr(chatlas, name, DummyChatClient)
