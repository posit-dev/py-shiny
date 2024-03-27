from __future__ import annotations

from typing import Optional

import pytest

from shiny import reactive, render
from shiny.render.renderer import Renderer, ValueFn
from shiny.session import Session, get_current_session


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
