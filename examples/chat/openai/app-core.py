from openai import OpenAI

from shiny import App, reactive, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select("model", "Model", choices=["gpt-4o", "gpt-3.5-turbo"]),
        ui.input_switch("streaming", "Stream", value=True),
        ui.input_slider("temperature", "Temperature", min=0, max=2, step=0.1, value=1),
        ui.input_slider("max_tokens", "Max Tokens", min=1, max=4096, step=1, value=256),
        position="right",
    ),
    ui.output_chat("chat"),
    title="OpenAI Chat Playground",
    fillable=True,
    fillable_mobile=True,
)


def server(input):

    @render.chat
    def chat():
        return render.Chat(
            messages=[{"content": "Hello! How can I help you?", "role": "assistant"}]
        )

    client = OpenAI()

    @reactive.effect
    @reactive.event(chat.user_input)
    async def _():
        messages = chat.messages()
        response = client.chat.completions.create(
            model=input.model(),
            messages=messages,
            stream=input.streaming(),
            temperature=input.temperature(),
            max_tokens=input.max_tokens(),
        )
        if input.streaming():
            await chat.append_message_stream(response)
        else:
            await chat.append_message(response)
            a


app = App(app_ui, server)
