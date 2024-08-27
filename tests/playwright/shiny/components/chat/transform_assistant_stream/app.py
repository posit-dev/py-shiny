from shiny import render
from shiny.express import ui

chat = ui.Chat(id="chat")
chat.ui()


@chat.transform_assistant_response
def transform(content: str, chunk: str, done: bool):
    if done:
        return content + "...DONE!"
    else:
        return content


@chat.on_user_submit
async def _():
    await chat.append_message_stream(("Simple ", "response"))


"Message state:"


@render.code
def message_state():
    return str(chat.messages())
