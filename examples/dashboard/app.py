import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from faicons import icon_svg
from shinywidgets import output_widget, render_widget

import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

pio.templates.default = "plotly_white"

app_ui = ui.page_navbar(
    ui.nav(
        "Overview",
        x.ui.layout_sidebar(
            x.ui.sidebar(
                ui.input_numeric("x", "X", 10),
                ui.input_slider("width", "Width", 0, 10, 5),
                ui.input_switch("switch", "Include all"),
            ),
            ui.head_content(ui.tags.style("html, body { height: 100%; }")),
            x.ui.layout_column_wrap(
                1 / 3,
                x.ui.value_box(
                    "Experiments run",
                    6,
                    showcase=icon_svg("flask", height="60px"),
                    theme_color="success",
                ),
                x.ui.value_box(
                    "Eggs",
                    10,
                    showcase=icon_svg("egg", height="60px"),
                    theme_color="primary",
                ),
                x.ui.value_box(
                    "Days remaining",
                    -2,
                    showcase=icon_svg("calendar-days", height="60px"),
                    theme_color="danger",
                ),
                fill=False,
                class_="mb-3",
            ),
            x.ui.layout_column_wrap(
                1,
                x.ui.card(
                    x.ui.card_header("Tip vs. day"),
                    output_widget("plot1", height="100%"),
                    x.ui.card_footer(ui.help_text("Data is updated weekly")),
                ),
                fill=True,
            ),
            fillable=True,
        ),
    ),
    title="Dashboard",
    bg="var(--bs-primary)",
    inverse=True,
    lang="en",
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render_widget
    def plot1():
        df = px.data.tips()
        fig = px.box(df, x="day", y="tip")
        return go.FigureWidget(fig)


app = App(app_ui, server)
