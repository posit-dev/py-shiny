from shared import mtcars

from shiny import reactive
from shiny.express import render, ui

df = reactive.value(mtcars.iloc[:, range(4)])


with ui.layout_columns(col_widths=[4, 4, 4]):
    with ui.card():
        with ui.card_header():
            ui.markdown(
                """
                ##### Editable data frame
                * Edit the cells!
                * Sort the columns!
                """
            )

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

    with ui.card():
        with ui.card_header():
            ui.markdown(
                """
                ##### Updated data from the first data frame
                * Select the rows!
                * Filter and sort the columns!
                """
            )

            @render.data_frame
            def df_edited():
                return render.DataGrid(
                    df_original.data_view(),
                    selection_mode="rows",
                    filters=True,
                )

    with ui.card():
        with ui.card_header():
            ui.markdown(
                """
                ##### Selected data from the second data frame
                * Sort the columns!
                """
            )

            @render.data_frame
            def df_selected():
                return render.DataGrid(
                    df_edited.data_view(selected=True),
                    selection_mode="none",
                )
