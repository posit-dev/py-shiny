from openai import OpenAI

from shiny import App, reactive, render, ui

client = OpenAI()

app_ui = ui.page_fillable(
    ui.output_chat("chat"),
    fillable_mobile=True,
)


def server(input):

    @render.chat
    def chat():
        return render.Chat(
            messages=[{"content": "Hello! How can I help you?", "role": "assistant"}]
        )

    @reactive.effect
    @reactive.event(chat.user_input)
    async def _():
        messages = chat.messages()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=False,
        )
        content = response.choices[0].message.content
        await chat.append_message(content)  # defaults to role is "assistant"


app = App(app_ui, server)
