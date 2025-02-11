import asyncio
from typing import Union

from shiny import reactive
from shiny.express import render, ui
from shiny.reactive import ExtendedTask

chat = ui.Chat("chat")

chat.ui()
chat.update_user_input(value="Press Enter to start the stream")


async def stream_generator():
    for i in range(10):
        await asyncio.sleep(0.25)
        yield f"Message {i} \n\n"


@chat.on_user_submit
async def _(message: str):
    stream = await chat.append_message_stream(stream_generator())
    current_stream.set(stream)


current_stream: reactive.value[Union[ExtendedTask[[], str], None]] = reactive.value(
    None
)


@render.code
def stream_result_ui():
    stream = current_stream()
    return stream.result() if stream else None
