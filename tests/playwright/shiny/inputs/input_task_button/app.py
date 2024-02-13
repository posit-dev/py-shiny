import asyncio
from datetime import datetime

from shiny import reactive, render
from shiny.express import input, ui

ui.h5("Current time")


@render.text()
def current_time() -> str:
    reactive.invalidate_later(0.1)
    return str(datetime.now().utcnow())


with ui.p():
    "Notice that the time above updates every second, even if you click the button below."


@ui.bind_task_button(button_id="btn_task")
@reactive.extended_task
async def slow_compute(a: int, b: int) -> int:
    await asyncio.sleep(1.5)
    return a + b


async def slow_input_compute(a: int, b: int) -> int:
    await asyncio.sleep(1.5)
    return a + b


with ui.layout_sidebar():
    with ui.sidebar():
        ui.input_numeric("x", "x", 1)
        ui.input_numeric("y", "y", 2)
        ui.input_task_button("btn_task", "Non-blocking task")
        ui.input_task_button("btn_block", "Block compute", label_busy="Blocking...")
        ui.input_action_button("btn_cancel", "Cancel")

    @reactive.Effect
    @reactive.event(input.btn_task, ignore_none=False)
    def handle_click():
        # slow_compute.cancel()
        slow_compute(input.x(), input.y())

    @reactive.Effect
    @reactive.event(input.btn_block, ignore_none=False)
    async def handle_click2():
        # slow_compute.cancel()
        await slow_input_compute(input.x(), input.y())

    @reactive.Effect
    @reactive.event(input.btn_cancel)
    def handle_cancel():
        slow_compute.cancel()

    ui.h5("Sum of x and y")

    @render.text
    def show_result():
        return str(slow_compute.result())
