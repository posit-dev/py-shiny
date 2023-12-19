import pandas as pd

from shiny import App, Inputs, Outputs, Session, render, ui

df = pd.DataFrame(
    dict(
        id=["one", "two", "three"],
        fname=["Alice", "Bob", "Charlie"],
        lname=["Smith", "Jones", "Brown"],
    )
).set_index(  # type: ignore
    "id",
    drop=False,
)

app_ui = ui.page_fluid(
    ui.p("Select rows in the grid, make sure the selected rows appear below."),
    ui.output_data_frame("grid"),
    ui.output_table("detail"),
    ui.output_text_verbatim("debug"),
    class_="p-3",
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.data_frame
    def grid():
        return render.DataGrid(
            df,
            row_selection_mode="multiple",
            height=350,
        )

    @render.table
    def detail():
        if (
            input.grid_selected_rows() is not None
            and len(input.grid_selected_rows()) > 0
        ):
            # "split", "records", "index", "columns", "values", "table"
            return df.iloc[list(input.grid_selected_rows())]

    @render.text
    def debug():
        return input.grid_selected_rows()


app = App(app_ui, server, debug=True)
