import asyncio

from shiny import reactive
from shiny.express import input, render, ui

SLEEP_TIME = 0.75

ui.page_opts(title="Hello chat message streams")

with ui.sidebar(style="height:100%"):
    ui.input_action_button("basic_stream", "Add message stream")
    ui.input_action_button("nested_stream", "Add nested stream")

    ui.h6("Message state:", class_="mt-auto mb-0")

    @render.code
    def message_state():
        return str(chat.messages())


chat = ui.Chat(id="chat")
chat.ui()


# TODO: test submitting input after adding stream
@chat.on_user_submit
async def _(user_input: str):
    await chat.append_message(f"You said: {user_input}")


@reactive.effect
@reactive.event(input.basic_stream)
async def _():
    chunks = [
        "Starting stream 1 🔄...\n\n",
        "Progress: 0%",
        " Progress: 50%",
        " Progress: 100%",
    ]
    async with chat.message_stream():
        for chunk in chunks:
            await chat.append_message_chunk(chunk)
            await asyncio.sleep(SLEEP_TIME)
        await chat.append_message_chunk("Completed stream 1 ✅", operation="replace")


# TODO: add test here for nested .message_stream()


@reactive.effect
@reactive.event(input.nested_stream)
async def _():
    await chat.append_message_stream(mock_stream())


async def mock_stream():
    yield "Starting outer stream...\n\n"
    await asyncio.sleep(SLEEP_TIME)
    await mock_tool()
    await asyncio.sleep(SLEEP_TIME)
    yield "\n\n...outer stream complete"


async def mock_tool():
    chunks = [
        "Starting inner stream 🔄...\n\n",
        "Progress: 0%",
        " Progress: 50%",
        " Progress: 100%",
    ]
    for chunk in chunks:
        await chat.append_message_chunk(chunk, operation="replace")


# TODO: more tests, like submitting input, etc.
