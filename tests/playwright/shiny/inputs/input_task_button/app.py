import asyncio
import time
from datetime import datetime, timezone

from shiny import reactive, render
from shiny.express import input, ui

# Timestamps of every current_time render, used to verify that no renders
# happen while the session is blocked.
render_times: list[float] = []

# One entry per completed blocking computation: the number of current_time
# renders that ran inside that blocking window.
block_render_counts = reactive.value[tuple[int, ...]](())

# Start time of the most recent non-blocking (extended task) invocation, and
# one entry per completed invocation: the number of current_time renders that
# ran inside that non-blocking window. This is the negative control for
# block_render_counts: the session keeps flushing during an extended task, so
# these counts prove the render counter registers renders when they happen.
nonblock_start: list[float] = []
nonblock_render_counts = reactive.value[tuple[int, ...]](())

ui.h5("Current time")


@render.text()
def current_time() -> str:
    reactive.invalidate_later(0.1)
    render_times.append(time.time())
    return str(datetime.now(timezone.utc).isoformat())


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

    @reactive.effect
    @reactive.event(input.btn_task, ignore_none=False)
    def handle_click():
        # slow_compute.cancel()
        nonblock_start.append(time.time())
        slow_compute(input.x(), input.y())

    @reactive.effect
    def record_nonblock_window():
        slow_compute.result()  # Re-runs this effect when a result arrives
        t1 = time.time()
        count = sum(1 for t in render_times if nonblock_start[-1] < t < t1)
        # Isolate the read so appending does not re-trigger this effect.
        with reactive.isolate():
            counts = nonblock_render_counts()
        nonblock_render_counts.set(counts + (count,))

    @reactive.effect
    @reactive.event(input.btn_block, ignore_none=False)
    async def handle_click2():
        # slow_compute.cancel()
        t0 = time.time()
        await slow_input_compute(input.x(), input.y())
        t1 = time.time()
        # Renders queued while the session was blocked run after t1, so any
        # timestamp strictly inside the window is a render that happened
        # while this handler was (supposedly) blocking the session.
        count = sum(1 for t in render_times if t0 < t < t1)
        block_render_counts.set(block_render_counts() + (count,))

    @reactive.effect
    @reactive.event(input.btn_cancel)
    def handle_cancel():
        slow_compute.cancel()

    ui.h5("Sum of x and y")

    @render.text
    def show_result():
        return str(slow_compute.result())

    ui.h5("Time renders during each blocking window")

    @render.text
    def renders_during_block():
        return ",".join(str(count) for count in block_render_counts())

    ui.h5("Time renders during each non-blocking window")

    @render.text
    def renders_during_nonblock():
        return ",".join(str(count) for count in nonblock_render_counts())
