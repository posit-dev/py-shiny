import pkgutil

import palmerpenguins  # pyright: ignore[reportMissingTypeStubs]
import polars as pl
from narwhals.stable.v1.typing import IntoDataFrame

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui

pd_penguins = palmerpenguins.load_penguins_raw()
pl_penguins = pl.read_csv(
    pkgutil.get_data(  # pyright: ignore[reportArgumentType]
        "palmerpenguins", "data/penguins-raw.csv"
    )
)


def make_ui(title: str):
    return ui.card(
        title,
        ui.layout_columns(
            ui.input_select(
                "selection_mode",
                "Row Selection",
                choices=["rows", "row", "none"],
            ),
            ui.input_action_button("select", "Select 1, 3, 5"),
            ui.input_action_button("clear", "Clear selection"),
        ),
        ui.layout_columns(
            ui.h5("Selected Rows:"),
            ui.output_code("selected_rows"),
            ui.h5("Selected row count:"),
            ui.output_code("selected_row_count"),
            ui.h5("Total row count:"),
            ui.output_code("grid_row_count"),
        ),
        ui.hr(),
        ui.h5("Selected Data Frame"),
        ui.output_data_frame("grid_selected"),
        ui.h5("Data Frame"),
        ui.output_data_frame("grid"),
    )


def make_server(input: Inputs, data: IntoDataFrame):
    @render.data_frame
    def grid():
        return render.DataGrid(
            data=data,
            selection_mode=input.selection_mode(),
            height="300px",
        )

    @render.data_frame
    def grid_selected():
        return render.DataGrid(
            data=grid.data_view(selected=True),
            selection_mode=input.selection_mode(),
        )

    @reactive.effect
    @reactive.event(input.clear)
    async def clear():
        await grid.update_cell_selection(None)

    @reactive.effect
    @reactive.event(input.select)
    async def select_1_3_5():
        await grid.update_cell_selection({"type": "row", "rows": (1, 3, 5)})

    @render.code
    def selected_rows():
        return str(grid.cell_selection()["rows"])

    # Test for selected rows data
    @render.code
    def grid_row_count():
        nrow = grid._nw_data().shape[0]
        return str(nrow)

    @render.code
    def selected_row_count():
        nrow = grid_selected._nw_data().shape[0]
        return str(nrow)


@module.ui
def mod_ui(title: str = "Module"):
    return make_ui(title)


@module.server
def mod_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    data: IntoDataFrame,
):
    make_server(input, data)


app_ui = ui.page_fluid(
    make_ui("global"),
    mod_ui("pandas", "Module - pandas"),
    mod_ui("polars", "Module - polars"),
)


def server(input: Inputs, output: Outputs, session: Session):
    make_server(input, pd_penguins)

    mod_server("pandas", pd_penguins)

    mod_server("polars", pl_penguins)


app = App(app_ui, server)
