import asyncio

from shiny import reactive
from shiny.express import input, render, ui

stream = ui.MarkdownStream("stream_id")
stream.ui()


ui.input_action_button("do_stream", "Do stream")


async def gen():
    yield "Hello "
    await asyncio.sleep(0.1)
    yield "world!"


@reactive.effect
@reactive.event(input.do_stream)
async def _():
    await stream.stream(gen())


@render.code
def stream_result():
    res = stream.latest_stream.result()
    return f"Stream result: {res}"
