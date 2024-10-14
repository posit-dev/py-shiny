import pandas as pd

from shiny import App, Inputs, reactive, render, ui

app_ui = ui.page_fluid(
    ui.output_data_frame("df1"),
    ui.output_text_verbatim("selected_rows", placeholder=True),
    ui.output_text_verbatim("cell_selection", placeholder=True),
)


def server(input: Inputs):
    df = reactive.Value(pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=["A", "B"]))

    @render.data_frame
    def df1():
        return render.DataGrid(df(), selection_mode="rows")

    @render.text
    def selected_rows():
        return f"Input selected rows: {input.df1_selected_rows()}"

    @render.text
    def cell_selection():
        return f"Cell selection rows: {df1.cell_selection()['rows']}"


app = App(app_ui, server)
