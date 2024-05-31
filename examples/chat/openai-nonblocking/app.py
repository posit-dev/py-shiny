from openai import AsyncOpenAI

from shiny import App, reactive, ui

# Create the LLM client (assumes OPENAI_API_KEY is set in the environment)
client = AsyncOpenAI()

app_ui = ui.page_fillable(
    ui.chat_ui(
        id="chat",
        messages=[{"content": "Hello! How can I help you today?", "role": "assistant"}],
    ),
    title="Hello OpenAI Chat",
    fillable_mobile=True,
)


def server(input, output, session):

    # Create a chat instance
    chat = ui.Chat(id="chat")

    # Wrap the response creation/appending in an extended task
    # for non-blocking execution
    @reactive.extended_task
    async def response_task(messages):
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages, stream=True
        )
        return await chat.append_message_stream(response)

    @chat.on_user_submit
    async def _():
        response_task(chat.messages())


app = App(app_ui, server)
