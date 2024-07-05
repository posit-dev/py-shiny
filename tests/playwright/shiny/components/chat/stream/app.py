from shiny import reactive
from shiny.express import render, ui

ui.page_opts(title="Hello Chat")

# Create and display the chat
chat = ui.Chat(id="chat")
chat.ui()


@reactive.effect
async def _():
    await chat.append_message_stream(("FIRST ", "FIRST ", "FIRST"))


@reactive.effect
async def _():
    await chat.append_message("SECOND SECOND SECOND")


@reactive.effect
async def _():
    await chat.append_message_stream(("THIRD ", "THIRD ", "THIRD"))


@reactive.effect
async def _():
    await chat.append_message("FOURTH FOURTH FOURTH")


@reactive.effect
async def _():
    await chat.append_message_stream(("FIFTH ", "FIFTH ", "FIFTH"))


"Message state:"


@render.code
def message_state():
    return str(chat.messages())
