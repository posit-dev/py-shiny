import asyncio

from shiny import reactive
from shiny.express import input, render, ui

ui.page_opts(title="Hello Chat")

chat = ui.Chat(id="chat")
chat.ui()


async def generator():
    yield "Starting stream..."
    await asyncio.sleep(0.5)
    yield "...stream complete"


@reactive.effect
async def _():
    await chat.append_message_stream(generator())


@reactive.effect
async def _():
    await chat.append_message_chunk("injected chunk")


ui.input_action_button("run_test", "Run test")


@reactive.effect
@reactive.event(input.run_test)
async def _():
    await chat.start_message_stream()
    for chunk in ["can ", "inject ", "chunks"]:
        await asyncio.sleep(0.2)
        await chat.append_message_chunk(chunk)
    await chat.end_message_stream()


ui.input_action_button("run_test2", "Run test 2")


@reactive.effect
@reactive.event(input.run_test2)
async def _():
    await chat.append_message_stream(["can ", "append ", "chunks"])


@render.code
def message_out():
    return str(chat.messages())
