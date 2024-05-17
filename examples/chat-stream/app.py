from openai import OpenAI

from shiny import App, reactive, render, ui

client = OpenAI()

app_ui = ui.page_fillable(
    ui.download_button("download", "Download"),
    ui.output_chat("chat"),
    fillable_mobile=True,
)


def server(input):

    @render.download(filename="chat.csv")
    async def download():
        yield "one,two,three\n"
        yield "新,1,2\n"
        yield "型,4,5\n"

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
            model="gpt-4o", messages=messages, stream=True
        )
        await chat.append_message_stream(response)


app = App(app_ui, server)
