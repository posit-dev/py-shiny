from palmerpenguins import load_penguins_raw  # pyright: ignore[reportMissingTypeStubs]

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui


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


def make_server(input: Inputs):
    @render.data_frame
    def grid():
        return render.DataGrid(
            data=load_penguins_raw(),
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
        cell_selection = grid.cell_selection()
        if cell_selection is None:
            return "None"
        return str(cell_selection.get("rows", ()))

    # Test for selected rows data
    @render.code
    def grid_row_count():
        grid_data = grid.data()
        return str(grid_data.index.size)  # pyright: ignore[reportUnknownMemberType]

    @render.code
    def selected_row_count():
        grid_selected_data = grid_selected.data()
        return str(
            grid_selected_data.index.size  # pyright: ignore[reportUnknownMemberType]
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
