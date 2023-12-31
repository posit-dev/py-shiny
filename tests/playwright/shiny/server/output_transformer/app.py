from __future__ import annotations

from typing import Optional, overload

from shiny import App, Inputs, Outputs, Session, ui
from shiny.render.transformer import (
    TransformerMetadata,
    ValueFn,
    is_async_callable,
    output_transformer,
    resolve_value_fn,
)


@output_transformer
async def TestTextTransformer(
    _meta: TransformerMetadata,
    _fn: ValueFn[str | None],
    *,
    extra_txt: Optional[str] = None,
) -> str | None:
    value = await resolve_value_fn(_fn)
    value = str(value)
    value += "; "
    value += "async" if is_async_callable(_fn) else "sync"
    if extra_txt:
        value = value + "; " + str(extra_txt)
    return value


@overload
def render_test_text(
    *, extra_txt: Optional[str] = None
) -> TestTextTransformer.OutputRendererDecorator:
    ...


@overload
def render_test_text(
    _fn: TestTextTransformer.ValueFn,
) -> TestTextTransformer.OutputRenderer:
    ...


def render_test_text(
    _fn: TestTextTransformer.ValueFn | None = None,
    *,
    extra_txt: Optional[str] = None,
) -> TestTextTransformer.OutputRenderer | TestTextTransformer.OutputRendererDecorator:
    return TestTextTransformer(
        _fn,
        TestTextTransformer.params(extra_txt=extra_txt),
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
    @render_test_text
    def t1():
        return "t1; no call"
        # return "hello"

    @render_test_text
    async def t2():
        return "t2; no call"

    @render_test_text()
    def t3():
        return "t3; call"

    @render_test_text()
    async def t4():
        return "t4; call"

    @render_test_text(extra_txt="w/ extra_txt")
    def t5():
        return "t5; call"

    @render_test_text(extra_txt="w/ extra_txt")
    async def t6():
        return "t6; call"


app = App(app_ui, server)
