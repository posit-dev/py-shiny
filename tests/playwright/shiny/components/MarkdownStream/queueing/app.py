import asyncio

from shiny import reactive
from shiny.express import ui

stream = ui.MarkdownStream("stream")
stream.ui()


async def gen1():
    yield "First "
    await asyncio.sleep(0.1)
    yield "stream "


async def gen2():
    yield "Second "
    await asyncio.sleep(0.1)
    yield "stream "


@reactive.effect
async def _():
    await stream.stream(gen1())
    await stream.stream(gen2(), clear=False)
