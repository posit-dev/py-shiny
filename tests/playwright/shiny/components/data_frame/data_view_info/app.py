# pyright: reportUnknownMemberType = false
# pyright: reportMissingTypeStubs = false
# pyright: reportArgumentType = false
# pyright: reportUnknownMemberType = false

from palmerpenguins import load_penguins_raw

from shiny import App, Inputs, Outputs, Session, module, render, ui

# Load the dataset
penguins = load_penguins_raw().head(5)[["Sample Number", "Individual ID", "Date Egg"]]
df = penguins
MOD_ID = "testing"


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
                ),
                ui.output_data_frame("penguins_df"),
                width=1 / 2,
            )
        ),
    )


app_ui = ui.page_fillable(
    {"class": "p-3"},
    mod_ui(MOD_ID),
)


@module.server
def mod_server(input: Inputs, output: Outputs, session: Session):
    @render.data_frame
    def penguins_df():
        # return df
        return render.DataGrid(
            df,
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
        return str(penguins_df.input_column_sort())

    @render.code
    def filter():
        return str(penguins_df.input_column_filter())

    @render.code
    def rows():
        return str(penguins_df.data_view_rows())

    @render.code
    def selected_rows():
        cell_selection = penguins_df.input_cell_selection()
        if cell_selection is None:
            return ""
        return str(cell_selection.get("rows", ()))


def server(input: Inputs, output: Outputs, session: Session):
    mod_server(MOD_ID)


app = App(app_ui, server, debug=False)
app.sanitize_errors = True
