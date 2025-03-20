from datetime import datetime
from zoneinfo import ZoneInfo

from shiny import App, reactive, render, ui

# Define a consistent timezone
TIMEZONE = ZoneInfo("UTC")

app_ui = ui.page_fluid(
    ui.panel_title("Slider Parameters Demo"),
    ui.layout_column_wrap(
        # Numeric Slider - basic parameters
        ui.card(
            ui.card_header("Basic Numeric Slider"),
            ui.input_slider("slider1", "Min, max, value", min=0, max=100, value=50),
            ui.output_text("value1"),
        ),
        # Numeric Slider with step
        ui.card(
            ui.card_header("Step Parameter"),
            ui.input_slider(
                "slider2", "Step size = 10", min=0, max=100, value=50, step=10
            ),
            ui.output_text("value2"),
        ),
        # Range Slider
        ui.card(
            ui.card_header("Range Slider"),
            ui.input_slider(
                "slider3", "Select a range", min=0, max=100, value=(30, 70)
            ),
            ui.output_text("value3"),
        ),
        # Date Slider
        ui.card(
            ui.card_header("Date Slider"),
            ui.input_slider(
                "slider4",
                "Select a date",
                min=datetime(2023, 1, 1, 0, 0, tzinfo=TIMEZONE),
                max=datetime(2023, 12, 31, 0, 0, tzinfo=TIMEZONE),
                value=datetime(2023, 6, 15, 12, 30, tzinfo=TIMEZONE),
                time_format="%Y-%m-%d",
            ),
            ui.output_text("value4"),
        ),
        # Animated Slider
        ui.card(
            ui.card_header("Animated Slider"),
            ui.input_slider(
                "slider5", "With animation", min=0, max=100, value=50, animate=True
            ),
            ui.output_text("value5"),
        ),
        # Slider with custom formatting
        ui.card(
            ui.card_header("Custom Formatting"),
            ui.input_slider(
                "slider6",
                "With prefix and suffix",
                min=0,
                max=100,
                value=50,
                pre="$",
                post="%",
                sep=",",
            ),
            ui.output_text("value6"),
        ),
        # Slider with ticks
        ui.card(
            ui.card_header("Ticks Display"),
            ui.input_slider(
                "slider7", "With tick marks", min=0, max=100, value=50, ticks=True
            ),
            ui.output_text("value7"),
        ),
        # Date Range Slider with drag_range
        ui.card(
            ui.card_header("Date Range"),
            ui.input_slider(
                "slider9",
                "Draggable range",
                min=datetime(2023, 1, 1, 0, 0, tzinfo=TIMEZONE),
                max=datetime(2023, 12, 31, 0, 0, tzinfo=TIMEZONE),
                value=(
                    datetime(2023, 3, 1, 0, 0, tzinfo=TIMEZONE),
                    datetime(2023, 9, 30, 0, 0, tzinfo=TIMEZONE),
                ),
                time_format="%Y-%m-%d",
                timezone="UTC",
                drag_range=True,
            ),
            ui.output_text("value9"),
        ),
        # Datetime slider
        ui.card(
            ui.card_header("Datetime Slider"),
            ui.input_slider(
                "slider10",
                "With time format",
                min=datetime(2023, 1, 1, 0, 0, tzinfo=TIMEZONE),
                max=datetime(2023, 12, 31, 23, 59, tzinfo=TIMEZONE),
                value=datetime(2023, 6, 15, 12, 30, tzinfo=TIMEZONE),
                time_format="%Y-%m-%d %H:%M",
                timezone="UTC",
            ),
            ui.output_text("value10"),
        ),
        width="400px",
    ),
)


def server(input, output, session):
    @render.text
    @reactive.event(input.slider1)
    def value1():
        return f"Value: {input.slider1()}"

    @render.text
    @reactive.event(input.slider2)
    def value2():
        return f"Value: {input.slider2()}"

    @render.text
    @reactive.event(input.slider3)
    def value3():
        return f"Value: {input.slider3()}"

    @render.text
    @reactive.event(input.slider4)
    def value4():
        return f"Value: {input.slider4()}"

    @render.text
    @reactive.event(input.slider5)
    def value5():
        return f"Value: {input.slider5()}"

    @render.text
    @reactive.event(input.slider6)
    def value6():
        return f"Value: {input.slider6()}"

    @render.text
    @reactive.event(input.slider7)
    def value7():
        return f"Value: {input.slider7()}"

    @render.text
    @reactive.event(input.slider9)
    def value9():
        return f"Value: {input.slider9()}"

    @render.text
    @reactive.event(input.slider10)
    def value10():
        return f"Value: {input.slider10()}"


app = App(app_ui, server)
