from __future__ import annotations

from typing import Optional, cast

import pytest

from shiny import reactive, render
from shiny._namespaces import ResolvedId, Root
from shiny.render.renderer import Renderer, ValueFn, output_binding_request_handler
from shiny.session import Outputs, Session, get_current_session


class _MockSession:
    ns: ResolvedId = Root
    _message_handlers = {}

    # This is needed so that Outputs don't throw an error.
    def _is_hidden(self, name: str) -> bool:
        return False


test_session = cast(Session, _MockSession())


class RendererWithSession(Renderer[str]):
    _session: Session | None

    def __init__(self, _fn: Optional[ValueFn[str]] = None):
        super().__init__(_fn)
        self._session = get_current_session()


@pytest.mark.asyncio
async def test_renderer_works():
    # No args works
    class test_renderer(RendererWithSession):
        async def transform(self, value: str) -> str:
            return value + " " + value

    @test_renderer()
    def txt_paren() -> str:
        return "Hello World!"

    val = await txt_paren.render()
    assert val == "Hello World! Hello World!"

    @test_renderer
    def txt_no_paren() -> str:
        return "Hello World!"

    val = await txt_no_paren.render()
    assert val == "Hello World! Hello World!"


@pytest.mark.asyncio
async def test_renderer_works_with_args():
    # No args works
    class test_renderer_with_args(RendererWithSession):
        def __init__(self, _fn: Optional[ValueFn[str]] = None, *, times: int = 2):
            super().__init__(_fn)
            self.times: int = times

        async def transform(self, value: str) -> str:
            values = [value for _ in range(self.times)]
            return " ".join(values)

    @test_renderer_with_args
    def txt2() -> str:
        return "42"

    @test_renderer_with_args(times=4)
    def txt4() -> str:
        return "42"

    val = await txt2.render()
    assert val == "42 42"
    val = await txt4.render()
    assert val == "42 42 42 42"


def test_effect():
    with pytest.raises(TypeError):

        @reactive.effect  # pyright: ignore[reportArgumentType]
        @render.text
        def my_output():
            return "42"


@pytest.mark.asyncio
async def test_output_handler():
    class test_renderer(RendererWithSession):
        async def transform(self, value: str) -> str:
            return str(value)

        _handle_not_callable: str = "ignored"

        async def _handle_not_marked(self, msg: str) -> str:
            raise NotImplementedError()

        @output_binding_request_handler
        async def _handle_test_fn(self, msg: str) -> str:
            return f"handled {msg}"

    # Set the output to the test session
    outputs = Outputs(test_session, Root, outputs={})
    test_session.output = outputs
    # Unrelated methods to make the test happy enough to pass
    test_session.on_ended = lambda *args: None  # pyright: ignore
    test_session._send_message_sync = lambda *args: None  # pyright: ignore

    @outputs
    @test_renderer
    def app_fn() -> str:
        return "ignored"

    ex_val = "test value"
    # Check for missing renderer
    with pytest.raises(RuntimeError, match="unknown Output Renderer"):
        await outputs._output_binding_request_handler("bad_id", "_", ex_val)

    # Check for missing handler on the renderer
    with pytest.raises(RuntimeError, match="does not have method"):
        await outputs._output_binding_request_handler(
            "app_fn", "does_not_exist", ex_val
        )

    # Check handler is callable
    with pytest.raises(RuntimeError, match="does not have callable method"):
        await outputs._output_binding_request_handler("app_fn", "not_callable", ex_val)

    # Check handler has been marked as an output handler
    with pytest.raises(RuntimeError, match="did not mark method"):
        await outputs._output_binding_request_handler("app_fn", "not_marked", ex_val)

    # Check handler returns the correct value
    val = await outputs._output_binding_request_handler("app_fn", "test_fn", ex_val)
    assert val == f"handled {ex_val}"
