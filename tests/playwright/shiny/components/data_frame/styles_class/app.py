from __future__ import annotations

import polars as pl

# pyright: reportMissingTypeStubs = false
from palmerpenguins import load_penguins_raw

from shiny import App, Inputs, render, ui
from shiny.render._data_frame_utils._styles import StyleInfo

# Load the dataset
penguins = load_penguins_raw()
df = penguins

df = df.iloc[0:5, 0:6]


df_styles: list[StyleInfo] = [
    {
        "class": "everywhere",
    },
    {
        "location": "body",
        "rows": [1, 2],
        "cols": "Species",
        "class": "species",
    },
]

app_ui = ui.page_fillable(
    ui.tags.style(
        """
        .everywhere {
            color: darkorange !important;
            font-weight: bold;
        }
        .species {
            background-color: lightblue !important;
        }
        """
    ),
    {"class": "p-3"},
    ui.card(
        ui.card_header("Pandas Styles List:"),
        ui.output_data_frame("pd_list_styles"),
        height="400px",
    ),
    ui.card(
        ui.card_header("Polars Styles List:"),
        ui.output_data_frame("pl_list_styles"),
        height="400px",
    ),
)


def server(input: Inputs):

    @render.data_frame
    def pd_list_styles():
        return render.DataTable(
            df,
            selection_mode=("rows"),
            editable=True,
            # filters=True,
            styles=df_styles,
        )

    @render.data_frame
    def pl_list_styles():

        return render.DataTable(
            pl.from_pandas(df),
            selection_mode=("rows"),
            editable=True,
            # filters=True,
            styles=df_styles,
        )


app = App(app_ui, server, debug=False)
