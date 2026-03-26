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


def test_renderer_rejects_function_with_params():
    with pytest.raises(TypeError, match="no required parameters"):

        @render.text  # pyright: ignore[reportArgumentType]
        def bad_render(x: int) -> str:
            return str(x)


def test_renderer_accepts_function_with_no_params():
    @render.text
    def good_render():
        return "hello"


def test_renderer_warns_function_with_default_params():
    with pytest.warns(UserWarning, match="parameter.*with default values: x"):

        @render.text
        def good_render(x: str = "hello") -> str:
            return x


def test_renderer_warning_includes_render_prefix():
    with pytest.warns(UserWarning, match="@render.text"):

        @render.text
        def good_render(x: str = "hello") -> str:
            return x


def test_renderer_error_includes_render_prefix():
    with pytest.raises(TypeError, match="@render.text"):

        @render.text  # pyright: ignore[reportArgumentType]
        def bad_render(x: int) -> str:
            return str(x)


# -- render.download validation -----------------------------------------------


def test_download_rejects_function_with_params():
    with pytest.raises(TypeError, match="no required parameters"):

        @render.download  # pyright: ignore[reportArgumentType]
        def bad_download(x: int) -> str:
            return str(x)


def test_download_accepts_function_with_no_params():
    @render.download
    def good_download():
        return "file.txt"


def test_download_warns_function_with_default_params():
    with pytest.warns(UserWarning, match="parameter.*with default values: x"):

        @render.download
        def good_download(x: str = "file.txt") -> str:
            return x


def test_renderer_warning_stacklevel_points_to_caller():
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        @render.text
        def my_render(x: str = "hello") -> str:
            return x

    assert len(w) == 1
    assert w[0].filename == __file__


def test_download_warning_stacklevel_points_to_caller():
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        @render.download
        def my_download(x: str = "file.txt") -> str:
            return x

    assert len(w) == 1
    assert w[0].filename == __file__


def test_effect():
    with pytest.raises(TypeError):

        @reactive.effect  # pyright: ignore[reportArgumentType]
        @render.text
        def my_output():
            return "42"
