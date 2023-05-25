from __future__ import annotations

import htmltools

import shiny.experimental as x
from shiny import App, ui


def outer_inner() -> tuple[htmltools.Tag, htmltools.Tag]:
    inner = ui.div(
        id="inner",
        style=htmltools.css(
            height="200px",
            border="3px blue solid",
        ),
    )
    outer = ui.div(
        inner,
        id="outer",
        style=htmltools.css(
            height="300px",
            border="3px red solid",
        ),
    )
    return outer, inner


outer0, inner0 = outer_inner()
outer1, inner1 = outer_inner()
outer2, inner2 = outer_inner()

x.ui.as_fillable_container(outer2)

x.ui.as_fillable_container(outer2)
x.ui.as_fill_item(inner2)


app_ui = ui.page_fluid(
    ui.markdown(
        """\
        # `as_fill_container()`

        For an item to fill its parent element,
        * the item must have `as_fill_item()` be called on it
        * the parent container must have `as_fillable_container()` called on it

        Iff both methods are called, the inner child will naturally expand into its parent container.
        """
    ),
    ui.row(
        ui.column(4, ui.h5("Default behavior")),
        ui.column(4, ui.h5(ui.markdown("`as_fill_container(red)`"))),
        ui.column(
            4,
            ui.h5(ui.markdown("`as_fill_item(blue)` + `as_fillable_container(red)`")),
        ),
    ),
    ui.row(
        ui.column(4, ui.div(outer0)),
        ui.column(4, ui.div(outer1)),
        ui.column(4, x.ui.as_fill_carrier(ui.span(outer2))),
    ),
)


app = App(app_ui, server=None)
