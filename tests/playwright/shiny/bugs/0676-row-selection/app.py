from __future__ import annotations

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
    ui.p(
        "Selected data: ",
        ui.output_data_frame("detail"),
    ),
    ui.p(
        "Selected rows: ",
        ui.output_code("selected_rows"),
    ),
    class_="p-3",
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.data_frame
    def grid():
        return render.DataGrid(
            df,
            selection_mode="rows",
            height=350,
        )

    @render.data_frame
    def detail():
        return grid.data_view(selected=True)

    @render.code
    def selected_rows():
        return str(grid.cell_selection()["rows"])


app = App(app_ui, server, debug=False)
