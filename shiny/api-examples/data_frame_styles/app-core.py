import pandas as pd

from shiny import App, Inputs, render, ui

green_styles = [
    {
        "rows": [2, 4],
        "cols": [2, 4],
        "style": {
            "background-color": "mediumspringgreen",
            "width": "300px",
            "height": "100px",
        },
    }
]

n = 6
df = pd.DataFrame(
    {
        "a": range(n),
        "b": range(n, n * 2),
        "c": range(n * 2, n * 3),
        "d": range(n * 3, n * 4),
        "e": range(n * 4, n * 5),
    }
)

hi_styles = [
    {
        # No `rows` or `cols` means apply to all cells
        "class": "posit-bg",
        "style": {
            "border": "transparent",
            "color": "transparent",
        },
    },
    {
        "rows": [3],
        "cols": [2],
        "class": "posit-blue-bg",
        "style": {
            "width": "100px",
            "height": "75px",
        },
    },
    {
        "cols": [1, 3, 5],
        "class": "posit-blue-bg",
    },
    {
        "cols": [7],
        "rows": [0, 1, 2, 3, 5],
        "class": "posit-orange-bg",
    },
]

n = 7
hi_pd = pd.DataFrame(
    {
        "a": range(n),
        "b": range(n, n * 2),
        "c": range(n * 2, n * 3),
        "d": range(n * 3, n * 4),
        "e": range(n * 4, n * 5),
        "f": range(n * 5, n * 6),
        "g": range(n * 6, n * 7),
        "h": range(n * 7, n * 8),
        "i": range(n * 8, n * 9),
    }
)


app_ui = ui.page_fillable(
    ui.h2("Data Frame with Styles applied to 4 cells"),
    ui.output_data_frame("my_df"),
    ui.hr(),
    ui.tags.style(
        ui.HTML(
            """
        .posit-bg {
            background-color: #242a26 ;
        }
        .posit-blue-bg {
            background-color: #447099 ;
        }
        .posit-orange-bg {
            background-color: #ED642F ;
        }
        """
        )
    ),
    ui.h2(
        "Custom styles applied to all cells within a data frame ", ui.HTML("&#128075;")
    ),
    ui.output_data_frame("hi_df"),
)


def server(input: Inputs):
    @render.data_frame
    def my_df():
        return render.DataGrid(
            df,
            styles=green_styles,
        )

    @render.data_frame
    def hi_df():
        return render.DataGrid(
            hi_pd,
            styles=hi_styles,
        )


app = App(app_ui, server)
