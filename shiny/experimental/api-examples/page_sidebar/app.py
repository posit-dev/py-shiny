from __future__ import annotations

import shiny.experimental as x
from shiny import App

app_ui = x.ui.page_sidebar(
    "Sidebar content",
    "Main content",
)

app = App(app_ui, server=None)
