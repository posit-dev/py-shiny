import pandas as pd
from palmerpenguins import load_penguins

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui


def make_ui(title: str):
    return ui.card(
        title,
        ui.layout_columns(
            ui.input_select(
                "selection_mode",
                "Row Selection",
                choices=["multiple", "single", "none"],
            ),
            ui.input_action_button("select", "Select 1, 3, 5"),
            ui.input_action_button("clear", "Clear selection"),
        ),
        ui.layout_columns(
            ui.h5("Selected Rows:"),
            ui.output_text_verbatim("selected_rows"),
            ui.h5("Selected Row count:"),
            ui.output_text_verbatim("selected_row_count"),
        ),
        ui.hr(),
        ui.h5("Selected Data Frame"),
        ui.output_data_frame("grid_selected"),
        ui.h5("Data Frame"),
        ui.output_data_frame("grid"),
    )


def make_server(input: Inputs):
    @render.data_frame
    def grid():
        return render.DataGrid(
            data=load_penguins(),
            row_selection_mode=input.selection_mode(),
        )

    @render.data_frame
    def grid_selected():
        return render.DataGrid(
            data=grid.data_selected_rows(),
            row_selection_mode=input.selection_mode(),
        )

    @reactive.effect
    @reactive.event(input.clear)
    async def clear():
        await grid.update_row_selection(None)

    @reactive.effect
    @reactive.event(input.select)
    async def select_1_3_5():
        await grid.update_row_selection([1, 3, 5])

    @render.code
    def selected_rows():
        return str(grid.input_selected_rows())

    # Test for selected rows data
    @render.code
    def selected_row_count():
        grid_data = grid.data_selected_rows()
        if grid_data is None:
            raise ValueError("No rows selected")
        grid_selected_data = grid_selected._data()
        if grid_selected_data is None:
            raise ValueError("No rows selected")
        return (
            "grid: "
            + str(grid_data.index.size)  # pyright: ignore[reportUnknownMemberType]
            + "; selected: "
            + str(
                grid_selected_data.index.size  # pyright: ignore[reportUnknownMemberType]
            )
        )


@module.ui
def mod_ui():
    return make_ui("Module")


@module.server
def mod_server(input: Inputs, output: Outputs, session: Session):
    make_server(input)


app_ui = ui.page_fluid(
    make_ui("global"),
    mod_ui("card2"),
)


def server(input: Inputs, output: Outputs, session: Session):
    make_server(input)

    mod_server("card2")


app = App(app_ui, server)
