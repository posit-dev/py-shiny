import pandas as pd

from shiny import App, Inputs, reactive, render, req, ui

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
        cell_selection = df1.cell_selection()
        if cell_selection is None:
            req(cell_selection)
            raise ValueError("Cell selection is None")
        if cell_selection["type"] != "row":
            raise ValueError(
                f"Cell selection type is not 'row': {cell_selection['type']}"
            )
        rows = cell_selection["rows"]
        return f"Cell selection rows: {rows}"


app = App(app_ui, server)
