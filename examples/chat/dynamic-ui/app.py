from openai import OpenAI

from shiny.express import input, render, ui

ui.input_select("model", "Model", choices=["gpt-4o", "gpt-3.5-turbo"])

client = OpenAI()


@render.ui
def chat_ui():
    input.model()
    chat = ui.Chat(id="chat")

    @chat.on_user_submit
    async def _():
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=chat.messages(),
            stream=True,
        )
        await chat.append_message_stream(response)

    return chat
