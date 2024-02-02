from __future__ import annotations

import htmltools

from shiny import App, ui
from shiny.ui import fill


def outer_inner() -> htmltools.Tag:
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
    return outer


outer0 = outer_inner()

outer1 = outer_inner()
outer1.children[0] = fill.as_fill_item(outer1.children[0])

outer2 = outer_inner()
outer2 = fill.as_fillable_container(outer2)
outer2.children[0] = fill.as_fill_item(outer2.children[0])


app_ui = ui.page_fluid(
    ui.markdown(
        """\
        # `as_fill_item()`

        For an item to fill its parent element,
        * the item must have `as_fill_item()` be called on it
        * the parent container must have `as_fillable_container()` called on it

        If both methods are called, the inner child will naturally expand into its parent container.
        """
    ),
    ui.row(
        ui.column(4, ui.h5("Default behavior")),
        ui.column(4, ui.h5(ui.markdown("`as_fill_item(blue)`"))),
        ui.column(
            4,
            ui.h5(ui.markdown("`as_fill_item(blue)` + `as_fillable_container(red)`")),
        ),
    ),
    ui.row(
        ui.column(4, ui.div(outer0)),
        ui.column(4, ui.div(outer1)),
        ui.column(4, ui.span(outer2)),
    ),
)


app = App(app_ui, server=None)
