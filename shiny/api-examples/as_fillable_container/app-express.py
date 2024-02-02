from __future__ import annotations

from htmltools import Tag, css

from shiny.express import ui
from shiny.express.ui import fill

ui.markdown(
    """\
    # `as_fillable_container()`

    For an item to fill its parent element,
    * the item must have `as_fill_item()` be called on it
    * the parent container must have `as_fillable_container()` called on it

    If both methods are called, the inner child will naturally expand into its parent container.
    """
)


def outer_inner() -> Tag:
    inner = ui.div(
        id="inner",
        style=css(
            height="200px",
            border="3px blue solid",
        ),
    )
    outer = ui.div(
        inner,
        id="outer",
        style=css(
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

with ui.layout_columns():
    ui.markdown("##### Default behavior")
    ui.markdown("##### `as_fill_item(blue)`")
    ui.markdown("##### `as_fill_item(blue)` + `as_fillable_container(red)`")

with ui.layout_columns():
    outer0
    outer1
    outer2
