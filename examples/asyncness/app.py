import asyncio
import time
from pathlib import Path

from shiny import App, reactive, render, req, ui

app_ui = ui.page_fluid(
    ui.p(
        "Launch this app in two different tabs. In one tab, press the button and see if"
        " the clock stops in the other tab."
    ),
    ui.input_task_button("block", "Perform blocking operation"),
    ui.output_text("fast"),
)


def server(input, output, session):
    @render.text
    def fast():
        reactive.invalidate_later(1)
        return time.strftime("%H:%M:%S", time.localtime())

    @reactive.effect
    @reactive.event(input.block)
    async def slow():
        print("Starting slow operation")
        await asyncio.sleep(3)
        print("Slow operation finished")


app = App(app_ui, server, static_assets=Path(__file__).parent / "www")
