from palmerpenguins import load_penguins_raw  # pyright: ignore[reportMissingTypeStubs]

from shiny import App, Inputs, Outputs, Session, render, ui

df = load_penguins_raw()

df["Species"] = df["Species"].apply(lambda x: ui.HTML(f"<u>{x}</u>"))  # pyright: ignore


app_ui = ui.page_fluid(
    ui.h2("Palmer Penguins"),
    ui.output_data_frame("penguins_df"),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @render.data_frame
    def penguins_df():
        return render.DataGrid(
            data=df,  # pyright: ignore[reportUnknownArgumentType]
            editable=True,
            selection_mode="rows",
        )


app = App(app_ui, server)
