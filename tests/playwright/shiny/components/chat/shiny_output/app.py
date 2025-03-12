import ipyleaflet as ipyl  # pyright: ignore[reportMissingTypeStubs]
import pandas as pd
import plotly.express as px  # pyright: ignore[reportMissingTypeStubs]
from shinywidgets import render_plotly, render_widget

from shiny import reactive, render
from shiny.express import ui

ui.page_opts(
    title="Hello output bindings in Chat",
    fillable=True,
    fillable_mobile=True,
)

with ui.hold() as map_ui:

    @render_widget
    def map():
        return ipyl.Map(center=(52, 10), zoom=8)


chat = ui.Chat(
    id="chat",
    messages=[map_ui],
)

chat.ui()

with ui.hold() as df_1:

    @render.data_frame
    def df1():
        dat = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        return render.DataTable(dat, height="auto")


@reactive.effect
async def _():
    await chat.append_message(df_1)


with ui.hold() as df_2:

    @render.data_frame
    def df2():
        dat = pd.DataFrame({"c": [1, 2, 3], "d": [4, 5, 6]})
        return render.DataGrid(dat, selection_mode="rows")


@reactive.effect
async def _():
    await chat.append_message_stream(df_2)


with ui.hold() as plot_ui:

    @render_plotly
    def plot():
        dat = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        return px.scatter(dat, x="x", y="y")  # pyright: ignore[reportUnknownMemberType]


@reactive.effect
async def _():
    await chat.append_message_stream(plot_ui)


@render.code
def selected_data():
    return str(df2.data_view(selected=True))
