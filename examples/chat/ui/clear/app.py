from langchain_openai import ChatOpenAI

from shiny import reactive
from shiny.express import input, ui

ui.page_opts(
    title="Hello OpenAI Chat",
    fillable=True,
    fillable_mobile=True,
)

with ui.sidebar():
    ui.input_select("model", "Model", ["gpt-4o", "gpt-3.5-turbo"])

chat = ui.Chat(id="chat")
chat.ui()

# Create the LLM client (assumes OPENAI_API_KEY is set in the environment)
client = ChatOpenAI()


@chat.on_user_submit
async def _():
    response = await client.astream(chat.get_messages())
    await chat.append_message_stream(response)


# Clear the chat when the model changes
@reactive.effect
@reactive.event(input.model)
async def _():
    await chat.clear_messages()
