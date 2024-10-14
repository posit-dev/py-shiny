from __future__ import annotations

# pyright: reportUnknownMemberType = false
# pyright: reportMissingTypeStubs = false
# pyright: reportArgumentType = false
# pyright: reportUnknownMemberType = false
import polars as pl
from narwhals.stable.v1.typing import IntoDataFrame
from palmerpenguins import load_penguins_raw

from shiny import App, Inputs, Outputs, Session, module, render, ui

# Load the dataset
penguins = load_penguins_raw().head(5)[["Sample Number", "Individual ID", "Date Egg"]]
df = penguins


@module.ui
def mod_ui():
    return ui.TagList(
        ui.card(
            ui.layout_column_wrap(
                ui.TagList(
                    ui.div("Sort: ", ui.output_text_verbatim("sort")),
                    ui.div("Filter: ", ui.output_text_verbatim("filter")),
                    ui.div("Rows: ", ui.output_text_verbatim("rows")),
                    ui.div("Selected Rows: ", ui.output_text_verbatim("selected_rows")),
                    ui.div("Type: ", ui.output_text_verbatim("df_type")),
                ),
                ui.output_data_frame("penguins_df"),
                width=1 / 2,
            )
        ),
    )


app_ui = ui.page_fillable(
    ui.navset_card_underline(
        ui.nav_panel(
            "pandas",
            mod_ui("pandas"),
        ),
        ui.nav_panel(
            "polars",
            mod_ui("polars"),
        ),
        id="tab",
    ),
    title="Data Frame",
    id="navbar_id",
)


@module.server
def mod_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    dt: IntoDataFrame,
):
    @render.data_frame
    def penguins_df():
        # return df
        return render.DataGrid(
            dt,
            selection_mode="rows",
            editable=False,
            filters=True,
        )
        # return render.DataTable(df, selection_mode="none", editable=True)
        # return render.DataGrid(df, selection_mode="rows", editable=True)
        # return render.DataTable(df, selection_mode="rows", editable=True)
        return render.DataGrid(df, selection_mode="rows", editable=False)
        # return render.DataTable(df, selection_mode="rows", editable=False)

    @render.code
    def sort():
        return str(penguins_df.sort())

    @render.code
    def filter():
        return str(penguins_df.filter())

    @render.code
    def rows():
        return str(penguins_df.data_view_rows())

    @render.code
    def selected_rows():
        return str(penguins_df.cell_selection()["rows"])

    @render.code
    def df_type():
        return str(type(dt))


def server(input: Inputs, output: Outputs, session: Session):
    mod_server("pandas", dt=df)
    mod_server("polars", dt=pl.from_pandas(df))


app = App(app_ui, server, debug=False)
app.sanitize_errors = True
