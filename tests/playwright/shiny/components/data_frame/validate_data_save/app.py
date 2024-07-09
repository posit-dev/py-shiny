import time

from palmerpenguins import load_penguins_raw  # pyright: ignore[reportMissingTypeStubs]

from shiny import App, Inputs, Outputs, Session, render, ui
from shiny.render import CellPatch

app_ui = ui.page_fluid(
    ui.h2("Palmer Penguins"),
    ui.output_data_frame("penguins_df"),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @render.data_frame
    def penguins_df():
        return render.DataGrid(
            data=load_penguins_raw(),  # pyright: ignore[reportUnknownArgumentType]
            filters=True,
            editable=True,
        )

    @penguins_df.set_patch_fn
    async def upgrade_patch(
        *,
        patch: CellPatch,
    ):
        # Slow down change so that we can test for "editing" state
        time.sleep(2)
        return patch["value"]


app = App(app_ui, server)
