import asyncio

from shiny import reactive
from shiny.express import input, render, ui

ui.page_opts(title="Hello Chat")

chat = ui.Chat(id="chat")
chat.ui()


# Launch a stream on load
@reactive.effect
async def _():
    await chat.append_message_stream(mock_stream())


async def mock_stream():
    yield "Starting outer stream...\n\n"
    await asyncio.sleep(0.5)
    await mock_tool()
    await asyncio.sleep(0.5)
    yield "\n\n...outer stream complete"


# While the "outer" `.append_message_stream()` is running,
# start an "inner" stream with .message_stream()
async def mock_tool():
    steps = [
        "Starting inner stream 🔄...\n\n",
        "Progress: 0%...",
        "Progress: 50%...",
        "Progress: 100%...",
    ]
    async with chat.message_stream():
        for chunk in steps:
            await chat.append_message_chunk(chunk)
            await asyncio.sleep(0.5)
        await chat.append_message_chunk(
            "Completed inner stream ✅",
            operation="replace",
        )


@chat.on_user_submit
async def _(user_input: str):
    await chat.append_message_stream(f"You said: {user_input}")


ui.input_action_button("add_stream_basic", "Add .message_stream()")


@reactive.effect
@reactive.event(input.add_stream_basic)
async def _():
    async with chat.message_stream():
        await chat.append_message_chunk("Running test...")
        await asyncio.sleep(1)
        await chat.append_message_chunk("Test complete!")


# TODO: more tests, like submitting input, etc.


@render.code
def message_out():
    return str(chat.messages())
