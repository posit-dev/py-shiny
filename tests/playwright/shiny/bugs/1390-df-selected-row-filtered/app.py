import pandas as pd

from shiny.express import render, ui

df = pd.DataFrame(data={"a": [str(i) for i in range(10)]})


with ui.layout_column_wrap(width=1 / 2):
    with ui.card():
        ui.card_header("Original data")

        @render.data_frame
        def my_df():
            return render.DataGrid(data=df, filters=True, selection_mode="rows")

    with ui.card():
        ui.card_header("Selected data")

        @render.data_frame
        def selected_df():
            return my_df.data_view(selected=True)

    with ui.card():
        ui.card_header("Selected rows")

        @render.code
        def selected_rows():
            return str(my_df.cell_selection()["rows"])
