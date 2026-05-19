from __future__ import annotations

import pandas as pd

from shiny import App, Inputs, Outputs, Session, render, ui

df = pd.DataFrame(
    {
        "letter": ["a", "b", "c", "d", "e"],
        "number": [1, 2, 3, 4, 5],
    }
)

df_edit = pd.DataFrame(
    {
        "name": ["alpha", "beta", "gamma"],
        "value": [10, 20, 30],
    }
)

# Apparatus for the manual dark-mode screenshot harness on #1635.
# Runs before any other JS so `data-bs-theme` is set before the data grid
# mounts, letting an external screenshot driver switch themes
# deterministically via `?theme=light|dark` without animating the
# `input_dark_mode` toggle.
_theme_shim = ui.tags.script("""
    (function () {
      var p = new URLSearchParams(window.location.search).get('theme');
      if (p === 'dark' || p === 'light') {
        document.documentElement.setAttribute('data-bs-theme', p);
      }
    })();
    """)

app_ui = ui.page_fluid(
    ui.head_content(_theme_shim),
    ui.input_dark_mode(id="mode"),
    ui.h4("Selectable + filterable grid"),
    ui.output_data_frame("grid"),
    ui.h4("Editable grid"),
    ui.output_data_frame("grid_edit"),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @render.data_frame
    def grid():
        return render.DataGrid(df, filters=True, selection_mode="rows")

    @render.data_frame
    def grid_edit():
        return render.DataGrid(df_edit, editable=True)


app = App(app_ui, server)
