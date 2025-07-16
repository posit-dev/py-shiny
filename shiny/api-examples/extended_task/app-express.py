import asyncio
from datetime import datetime

from shiny import reactive, render
from shiny.express import input, ui

ui.h5("Current time")


@render.text
def current_time():
    reactive.invalidate_later(1)
    return datetime.now().strftime("%H:%M:%S")


with ui.p():
    "Notice that the time above updates every second, even if you click the button below."


@ui.bind_task_button(button_id="btn")
@reactive.extended_task
async def slow_compute(a: int, b: int) -> int:
    await asyncio.sleep(3)
    return a + b


with ui.layout_sidebar():
    with ui.sidebar():
        ui.input_numeric("x", "x", 1)
        ui.input_numeric("y", "y", 2)
        ui.input_task_button("btn", "Compute, slowly")
        ui.input_action_button("btn_cancel", "Cancel")

    @reactive.effect
    @reactive.event(input.btn, ignore_none=False)
    def handle_click():
        # slow_compute.cancel()
        slow_compute(input.x(), input.y())

    @reactive.effect
    @reactive.event(input.btn_cancel)
    def handle_cancel():
        slow_compute.cancel()

    ui.h5("Sum of x and y")

    @render.text
    def show_result():
        return str(slow_compute.result())
