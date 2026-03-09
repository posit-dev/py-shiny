import asyncio
import time
from pathlib import Path

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.p(
        "Launch this Shiny for Python app in two different tabs. In one tab, press the button and see if"
        " the clock stops in the other tab."
    ),
    ui.input_task_button("block", "Perform blocking operation"),
    ui.output_text("fast"),
)


def server(input, output, session):
    @render.text
    def fast():
        reactive.invalidate_later(0.1)
        return time.strftime("%H:%M:%S", time.localtime())

    def make_effect(i):
        @reactive.effect
        @reactive.event(input.block)
        async def _():
            print(f"Starting slow operation {i}")
            await asyncio.sleep(3)
            print(f"Slow operation {i} finished")

    for i in range(3):
        make_effect(i + 1)


app = App(app_ui, server, static_assets=Path(__file__).parent / "www")
