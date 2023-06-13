from __future__ import annotations

import shiny.experimental as x
from shiny import App, ui

y = x.ui.card("A simple card")

app_ui = ui.page_fluid(
    # Always has 2 columns (on non-mobile)
    x.ui.layout_column_wrap(1 / 2, y, y, y),
    ui.hr(),
    # Has three columns when viewport is wider than 750px
    x.ui.layout_column_wrap("250px", y, y, y),
)


app = App(app_ui, server=None)
