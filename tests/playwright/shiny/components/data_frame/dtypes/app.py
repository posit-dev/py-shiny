from dataclasses import dataclass
from datetime import date, datetime, timedelta

import pandas as pd
from htmltools import HTML, strong

from shiny import App, Inputs, render, ui


class C:
    x: int

    def __init__(self, x: int):
        self.x = x

    def __str__(self):
        return f"<{self.__class__.__name__} object>"


@dataclass
class D:
    y: int


DATA = {  # pyright: ignore[reportUnknownVariableType]
    "num": [1, 2],
    "chr": ["a", "b"],
    "cat": pd.Series(["c", "d"], dtype="category"),
    "bool": [True, False],
    "date": [date(2000, 1, 2)] * 2,
    "datetime": [datetime(2000, 1, 2)] * 2,
    "duration": [timedelta(weeks=1), timedelta(days=7)],
    "html": [strong("bolded content")] * 2,
    "html_str": [HTML("<strong>bolded string</strong>")] * 2,
    "struct": [{"x": 1}, {"x": 2}],
    "arr": [[1, 2], [3, 4]],
    "object": [C(1), D(2)],
}

df = pd.DataFrame(DATA)


@render.data_frame
def df_html():
    return df


app_ui = ui.page_fillable(
    ui.card(
        ui.output_data_frame("df_html"),
    )
)


def server(input: Inputs):
    @render.data_frame
    def df_html():
        return df


app = App(app_ui, server)
