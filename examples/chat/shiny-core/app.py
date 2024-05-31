from openai import AsyncOpenAI

from shiny import App, ui

app_ui = ui.page_fillable(
    ui.panel_title("Hello OpenAI Chat"), ui.chat_ui("chat"), fillable_mobile=True
)


def server(input, output, session):
    chat = ui.Chat("chat")
    client = AsyncOpenAI()

    @chat.on_user_submit
    async def _():
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=chat.messages(),
            stream=True,
        )
        await chat.append_message_stream(response)


app = App(app_ui, server)
