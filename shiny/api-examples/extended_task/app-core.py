import asyncio
from datetime import datetime

from shiny import App, reactive, render, ui

app_ui = ui.page_fixed(
    ui.h5("Current time"),
    ui.output_text("current_time"),
    ui.p(
        "Notice that the time above updates every second, even if you click the button below."
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_numeric("x", "x", 1),
            ui.input_numeric("y", "y", 2),
            ui.input_task_button("btn", "Compute, slowly"),
            ui.input_action_button("btn_cancel", "Cancel"),
        ),
        ui.h5("Sum of x and y"),
        ui.output_text("show_result"),
    ),
)


def server(input, output, session):
    @render.text
    def current_time():
        reactive.invalidate_later(1)
        return datetime.now().strftime("%H:%M:%S")

    @ui.bind_task_button(button_id="btn")
    @reactive.extended_task
    async def slow_compute(a: int, b: int) -> int:
        await asyncio.sleep(3)
        return a + b

    @reactive.effect
    @reactive.event(input.btn, ignore_none=False)
    def handle_click():
        slow_compute(input.x(), input.y())

    @reactive.effect
    @reactive.event(input.btn_cancel)
    def handle_cancel():
        slow_compute.cancel()

    @render.text
    def show_result():
        return str(slow_compute.result())


app = App(app_ui, server)
