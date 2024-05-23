from openai import OpenAI

from shiny import reactive
from shiny.express import input, ui

ui.page_opts(
    title="Hello OpenAI Chat",
    fillable=True,
    fillable_mobile=True,
)

with ui.sidebar():
    ui.input_select("model", "Model", ["gpt-4o", "gpt-3.5-turbo"])

# Create and display the chat
chat = ui.Chat(id="chat")

chat

# Create the LLM client (assumes OPENAI_API_KEY is set in the environment)
client = OpenAI()


# on user submit, generate and append a response
@chat.on_user_submit
async def _():
    response = client.chat.completions.create(
        model=input.model(),
        messages=chat.messages(),
        stream=True,
    )
    await chat.append_message_stream(response)


@reactive.effect
@reactive.event(input.model)
async def _():
    await chat.clear_messages()
