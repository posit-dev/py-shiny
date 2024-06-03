from palmerpenguins import load_penguins_raw  # pyright: ignore[reportMissingTypeStubs]

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.h2("Palmer Penguins"),
    ui.output_data_frame("penguins_df"),
    ui.output_code("selected_row_count"),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @render.data_frame
    def penguins_df():
        return render.DataGrid(
            data=load_penguins_raw(),  # pyright: ignore[reportUnknownArgumentType]
            filters=True,
            selection_mode="row",
        )

    @render.code
    def selected_row_count():
        # grid_selected_data = grid_selected.data()
        return str(
            penguins_df.data_view(selected=True)
        )  # pyright: ignore[reportUnknownMemberType]


app = App(app_ui, server)
