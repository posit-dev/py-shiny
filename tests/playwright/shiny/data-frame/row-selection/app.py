from palmerpenguins import load_penguins

from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

df = load_penguins()

app_ui = ui.page_fluid(
    ui.input_select(
        "selection_mode", "Row Selection", choices=["single", "multiple", "none"]
    ),
    ui.input_action_button("select", "Select 1, 3, 5"),
    ui.input_action_button("clear", "Clear selection"),
    ui.output_data_frame("grid"),
    ui.output_text_verbatim("selected_rows"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.data_frame
    def grid():
        return render.DataGrid(data=df, row_selection_mode=input.selection_mode())

    @reactive.effect
    @reactive.event(input.clear)
    async def clear():
        await grid.update_row_selection(None)

    @reactive.effect
    @reactive.event(input.select)
    async def select_1_3_5():
        await grid.update_row_selection([1, 2, 5])

    @render.text_verbatim
    def selected_rows():
        return input.grid_selected_rows()


app = App(app_ui, server)
