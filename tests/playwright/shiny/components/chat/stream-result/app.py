import asyncio

from shiny.express import render, ui

chat = ui.Chat("chat")

chat.ui()
chat.update_user_input(value="Press Enter to start the stream")


async def stream_generator():
    for i in range(10):
        await asyncio.sleep(0.25)
        yield f"Message {i} \n\n"


@chat.on_user_submit
async def _(message: str):
    await chat.append_message_stream(stream_generator())


@render.code
async def stream_result():
    return chat.latest_message_stream.result()
