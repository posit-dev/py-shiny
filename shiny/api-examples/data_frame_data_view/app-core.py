from shared import mtcars

from shiny import App, reactive, render, ui

app_ui = ui.page_fillable(
    ui.layout_columns(
        ui.card(
            ui.card_header(
                ui.markdown(
                    """
                    ##### Editable data frame
                    * Edit the cells!
                    * Sort the columns!
                    """
                )
            ),
            ui.output_data_frame("df_original"),
        ),
        ui.card(
            ui.card_header(
                ui.markdown(
                    """
                    ##### Updated data from the first data frame
                    * Select the rows!
                    * Filter and sort the columns!
                    """
                )
            ),
            ui.output_data_frame("df_edited"),
        ),
        ui.card(
            ui.card_header(
                ui.markdown(
                    """
                    ##### Selected data from the second data frame
                    * Sort the columns!
                    """
                )
            ),
            ui.output_data_frame("df_selected"),
        ),
        col_widths=[4, 4, 4],
    ),
)


def server(input, output, session):
    df = reactive.value(mtcars.iloc[:, range(4)])

    @render.data_frame
    def df_original():
        return render.DataGrid(
            df(),
            editable=True,
        )

    # Convert edited values to the correct data type
    @df_original.set_patch_fn
    def _(*, patch: render.CellPatch) -> render.CellValue:
        if patch["column_index"] in [0, 2]:
            return float(patch["value"])
        return int(patch["value"])

    @render.data_frame
    def df_edited():
        return render.DataGrid(
            # Reactive value is updated when the user edits the data within `df_original` output
            df_original.data_view(),
            selection_mode="rows",
            filters=True,
        )

    @render.data_frame
    def df_selected():
        return render.DataGrid(
            # Reactive value is updated when the user selects rows the data within `df_edited` output
            df_edited.data_view(selected=True),
            selection_mode="rows",
        )


app = App(app_ui, server)
