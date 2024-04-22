from openai import OpenAI

from shiny import App, chat, reactive, ui

client = OpenAI()

app_ui = ui.page_fillable(
    chat.box(
        id="chat_box",
        messages=chat.message("Hello! How can I help you?", role="assistant"),
    ),
    fillable_mobile=True,
)


def server(input):

    # TODO: this doesn't actually lead to a streaming effect because
    # Shiny still batches the messages together and sends them all at once
    # for some reason. Maybe this needs to use send_custom_message instead of send_input_message?
    @reactive.effect
    @reactive.event(input.chat_box, ignore_init=True)
    async def _():
        messages = input.chat_box()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            chat.insert_streaming_message("chat_box", content=content, role="assistant")


app = App(app_ui, server)
