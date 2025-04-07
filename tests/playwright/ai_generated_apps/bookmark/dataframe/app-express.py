from palmerpenguins import load_penguins

from shiny import reactive
from shiny.express import app_opts, input, render, session, ui

penguins = load_penguins()

app_opts(bookmark_store="url")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)


ui.h2("Palmer Penguins")

ui.h5("Current selection: ", {"class": "pt-2"})


@render.code
def _():
    return penguins_df.cell_selection()["rows"]


ui.br()


@render.data_frame
def penguins_df():
    return render.DataGrid(penguins, selection_mode="rows")


@render.text
def penguins_df_text():
    return f"Selection mode: rows - Selected: {penguins_df.cell_selection()['rows']}"


ui.br()


@render.data_frame
def penguins_row_df():
    return render.DataGrid(penguins, selection_mode="row")


@render.text
def penguins_row_df_text():
    return f"Selection mode: row - Selected: {penguins_row_df.cell_selection()['rows']}"


ui.br()


@render.data_frame
def penguins_filter_df():
    return render.DataGrid(penguins, filters=True)


@render.text
def penguins_filter_df_text():
    return f"Filters enabled - Selected: {penguins_filter_df.cell_selection()['rows']}"


ui.br()


@render.data_frame
def penguins_editable_df():
    return render.DataGrid(penguins, editable=True)


@render.text
def penguins_editable_df_text():
    return f"Editable grid - Selected: {penguins_editable_df.cell_selection()['rows']}"


ui.br()
