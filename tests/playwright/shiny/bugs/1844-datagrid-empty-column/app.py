import pandas as pd

from shiny import App, Inputs, reactive, render, ui

app_ui = ui.page_fluid(
    ui.output_data_frame("df1"),
)


def server(input: Inputs):
    df = reactive.Value(
        pd.DataFrame(
            {
                "": [1, 2],
                "A": [4, 5],
                " ": [7, 8],
            }
        )
    )

    @render.data_frame
    def df1():
        return render.DataGrid(df())


app = App(app_ui, server)
