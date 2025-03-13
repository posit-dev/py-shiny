import asyncio

from shiny import reactive
from shiny.express import input, render, ui

ui.page_opts(title="Hello message streams")

chat = ui.Chat(id="chat")
chat.ui()


# Launch a stream on load
@reactive.effect
async def _():
    await chat.append_message_stream(mock_stream())


SLEEP_TIME = 0.25


async def mock_stream():
    yield "Starting outer stream...\n\n"
    await asyncio.sleep(SLEEP_TIME)
    await mock_tool()
    await asyncio.sleep(SLEEP_TIME)
    yield "\n\n...outer stream complete"


async def mock_tool():
    # While the "outer" `.append_message_stream()` is running,
    # start an "inner" stream with .message_stream()
    async with chat.message_stream():
        await chat.append_message_chunk("\n\nStarting inner stream 1 🔄...")
        await asyncio.sleep(SLEEP_TIME)
        await chat.append_message_chunk("Progress: 0%")
        await asyncio.sleep(SLEEP_TIME)

        async with chat.message_stream():
            await chat.append_message_chunk("\n\nStarting nested stream 2 🔄...")
            await asyncio.sleep(SLEEP_TIME)
            await chat.append_message_chunk("Progress: 0%")
            await asyncio.sleep(SLEEP_TIME)
            await chat.append_message_chunk(" Progress: 50%")
            await asyncio.sleep(SLEEP_TIME)
            await chat.append_message_chunk(" Progress: 100%")
            await asyncio.sleep(SLEEP_TIME)
            await chat.append_message_chunk(
                "\n\nCompleted _another_ inner stream ✅", operation="replace"
            )

        await chat.append_message_chunk("\n\nBack to stream 1...")
        await chat.append_message_chunk(" Progress: 50%")
        await asyncio.sleep(SLEEP_TIME)
        await chat.append_message_chunk(" Progress: 100%")
        await asyncio.sleep(SLEEP_TIME)

        await chat.append_message_chunk(
            "\n\nCompleted inner _and nested_ stream ✅", operation="replace"
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
