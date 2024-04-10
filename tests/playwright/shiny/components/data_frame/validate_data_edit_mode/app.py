from palmerpenguins import load_penguins_raw  # pyright: ignore[reportMissingTypeStubs]

from shiny import App, Inputs, Outputs, Session, render, ui
from shiny.render._dataframe import CellPatch
from shiny.types import SafeException

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
            editable=True,
        )

    @render.code
    def selected_row_count():
        # grid_selected_data = grid_selected.data()
        return str(
            penguins_df.data_selected()  # pyright: ignore[reportUnknownMemberType]
        )

    @penguins_df.set_patch_fn
    async def upgrade_patch(
        *,
        patch: CellPatch,
    ):

        if (patch["column_index"] == 0) and (
            patch["value"] not in ["Adelie", "Chinstrap", "Gentoo"]
        ):  # check species
            raise SafeException(
                "Penguin species should be one of Adelie, Chinstrap, Gentoo"
            )
        if (patch["column_index"] == 2) and int(
            patch[
                "value"
            ]  # pyright: ignore[reportArgumentType,reportGeneralTypeIssues]
        ) > 50:  # check bill_length_mm
            raise SafeException("Penguin bill length cannot be greater than 50mm")
        return patch["value"]


app = App(app_ui, server)
