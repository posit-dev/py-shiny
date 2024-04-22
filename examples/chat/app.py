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
    @reactive.effect
    @reactive.event(input.chat_box, ignore_init=True)
    def _():
        messages = input.chat_box()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=False,
        )
        content = response.choices[0].message.content
        chat.insert_message("chat_box", content=content, role="assistant")


app = App(app_ui, server)
