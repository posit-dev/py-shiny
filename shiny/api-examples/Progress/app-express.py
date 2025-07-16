import asyncio

from shiny import reactive
from shiny.express import input, render, ui

ui.input_action_button("button", "Compute")


@render.text
@reactive.event(input.button)
async def compute():
    with ui.Progress(min=1, max=15) as p:
        p.set(message="Calculation in progress", detail="This may take a while...")

        for i in range(1, 15):
            p.set(i, message="Computing")
            await asyncio.sleep(0.1)
            # Normally use time.sleep() instead, but it doesn't yet work in Pyodide.
            # https://github.com/pyodide/pyodide/issues/2354

    return "Done computing!"
