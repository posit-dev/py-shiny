# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

from typing import Optional, overload

from shiny import App, Inputs, Outputs, Session, ui
from shiny.render._render import TransformerMetadata, ValueFnAsync, output_transformer


@output_transformer
async def _render_test_text_components(
    _meta: TransformerMetadata,
    _fn: ValueFnAsync[str | None],
    *,
    extra_txt: Optional[str] = None,
) -> str | None:
    value = await _fn()
    value = str(value)
    value += "; "
    value += "async" if _meta.is_async else "sync"
    if extra_txt:
        value = value + "; " + str(extra_txt)
    return value


@overload
def render_test_text(
    *, extra_txt: Optional[str] = None
) -> _render_test_text_components.OutputRendererDecorator:
    ...


@overload
def render_test_text(
    _fn: _render_test_text_components.ValueFn,
) -> _render_test_text_components.OutputRenderer:
    ...


def render_test_text(
    _fn: _render_test_text_components.ValueFnOrNone = None,
    *,
    extra_txt: Optional[str] = None,
) -> _render_test_text_components.OutputRendererOrDecorator:
    return _render_test_text_components.impl(
        _fn,
        _render_test_text_components.params(extra_txt=extra_txt),
    )


app_ui = ui.page_fluid(
    ui.code("t1:"),
    ui.output_text_verbatim("t1"),
    ui.code("t2:"),
    ui.output_text_verbatim("t2"),
    ui.code("t3:"),
    ui.output_text_verbatim("t3"),
    ui.code("t4:"),
    ui.output_text_verbatim("t4"),
    ui.code("t5:"),
    ui.output_text_verbatim("t5"),
    ui.code("t6:"),
    ui.output_text_verbatim("t6"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render_test_text
    def t1():
        return "t1; no call"
        # return "hello"

    @output
    @render_test_text
    async def t2():
        return "t2; no call"

    @output
    @render_test_text()
    def t3():
        return "t3; call"

    @output
    @render_test_text()
    async def t4():
        return "t4; call"

    @output
    @render_test_text(extra_txt="w/ extra_txt")
    def t5():
        return "t5; call"

    @output
    @render_test_text(extra_txt="w/ extra_txt")
    async def t6():
        return "t6; call"


app = App(app_ui, server)
