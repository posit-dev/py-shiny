from __future__ import annotations

import htmltools

import shiny.experimental as x
from shiny import App, ui


def outer_inner() -> tuple[htmltools.Tag, htmltools.Tag, htmltools.Tag]:
    inner = ui.div(
        id="inner",
        style=htmltools.css(
            height="200px",
            border="3px blue solid",
        ),
    )
    middle = ui.div(
        inner,
        id="middle",
        style=htmltools.css(
            height="300px",
            border="3px green solid",
        ),
    )
    outer = ui.div(
        middle,
        id="outer",
        style=htmltools.css(
            height="400px",
            border="3px red solid",
        ),
    )
    return outer, middle, inner


# outer0, inner0 = outer_inner()

outer0, middle0, inner0 = outer_inner()
outer1, middle1, inner1 = outer_inner()
outer2, middle2, inner2 = outer_inner()
outer3, middle3, inner3 = outer_inner()
x.ui.as_fillable_container(outer0)
x.ui.as_fillable_container(outer1)
x.ui.as_fillable_container(outer2)
x.ui.as_fillable_container(outer3)

x.ui.as_fill_item(inner0)
x.ui.as_fill_item(inner1)
x.ui.as_fill_item(inner2)
x.ui.as_fill_item(inner3)

x.ui.as_fill_item(middle1)
x.ui.as_fillable_container(middle2)
x.ui.as_fill_carrier(middle3)

app_ui = ui.page_fluid(
    ui.markdown(
        """\
        # `as_fill_carrier()`

        For an element to pass through the ability to fill layout,
        * the element must have `as_fill_item(el)` be called to allow it to expand
        * the element must have `as_fillable_container(el)` called on it to allow its contents to expand

        This can be shortened by calling `as_fill_carrier(el)`.

        For all examples below,
        * `as_fillable_container(red)` has been called, allowing its contents to naturally expand.
        * `as_fill_item(blue)` has been called, allowing it to expand into its parent container
        """
    ),
    ui.row(
        ui.column(3, ui.h5("Default")),
        ui.column(3, ui.h5(ui.markdown("`as_fill_item(green)`"))),
        ui.column(3, ui.h5(ui.markdown("`as_fillable_container(green)`"))),
        ui.column(3, ui.h5(ui.markdown("`as_fill_carrier(green)`"))),
    ),
    ui.row(
        ui.column(3, ui.div(outer0)),
        ui.column(3, ui.div(outer1)),
        ui.column(3, ui.div(outer2)),
        ui.column(3, ui.div(outer3)),
    ),
)

app = App(app_ui, server=None)
