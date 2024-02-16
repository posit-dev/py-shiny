import pandas as pd
from palmerpenguins import load_penguins

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui


@module.ui
def mod_ui():
    return ui.card(
        "Module",
        ui.layout_columns(
            ui.input_select(
                "selection_mode",
                "Row Selection",
                choices=["multiple", "single", "none"],
            ),
            ui.input_action_button("select", "Select 1, 3, 5"),
            ui.input_action_button("clear", "Clear selection"),
            ui.output_text_verbatim("selected_rows"),
        ),
        ui.output_data_frame("grid"),
    )


@module.server
def mod_server(input: Inputs, output: Outputs, session: Session):
    @render.data_frame
    def grid():
        return render.DataGrid(
            data=load_penguins(), row_selection_mode=input.selection_mode()
        )

    @reactive.effect
    @reactive.event(input.clear)
    async def clear():
        await grid.update_row_selection(None)

    @reactive.effect
    @reactive.event(input.select)
    async def select_1_3_5():
        await grid.update_row_selection([1, 3, 5])

    @render.text
    def selected_rows():
        return input.grid_selected_rows()


app_ui = ui.page_fluid(
    ui.card(
        "No module",
        ui.layout_columns(
            ui.input_select(
                "selection_mode",
                "Row Selection",
                choices=["multiple", "single", "none"],
            ),
            ui.input_action_button("select", "Select 1, 3, 5"),
            ui.input_action_button("clear", "Clear selection"),
            ui.output_text_verbatim("selected_rows"),
        ),
        ui.output_data_frame("grid"),
    ),
    mod_ui("card2"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.data_frame
    def grid():
        return render.DataGrid(
            data=load_penguins(), row_selection_mode=input.selection_mode()
        )

    @reactive.effect
    @reactive.event(input.clear)
    async def clear():
        await grid.update_row_selection(None)

    @reactive.effect
    @reactive.event(input.select)
    async def select_1_3_5():
        await grid.update_row_selection([1, 3, 5])

    @render.text
    def selected_rows():
        return input.grid_selected_rows()

    mod_server("card2")


app = App(app_ui, server)
