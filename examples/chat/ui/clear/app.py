# --------------------------------------------------------------------------------
# This example demonstrates how to clear the chat when the model changes.
# To run it, you'll need an OpenAI API key.
# To get one, follow the instructions at https://platform.openai.com/docs/quickstart
# --------------------------------------------------------------------------------
import os

from langchain_openai import ChatOpenAI

from shiny import reactive
from shiny.express import input, ui

# Provide your API key here (or set the environment variable)
llm = ChatOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # type: ignore
)

# Set some Shiny page options
ui.page_opts(
    title="Hello OpenAI Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create a sidebar to select the model
with ui.sidebar():
    ui.input_select("model", "Model", ["gpt-4o", "gpt-3.5-turbo"])

# Create and display an empty chat UI
chat = ui.Chat(id="chat")
chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _():
    # Get messages currently in the chat
    messages = chat.messages(format="langchain")
    # Create a response message stream
    response = llm.astream(messages)
    # Append the response stream into the chat
    await chat.append_message_stream(response)


# Clear the chat when the model changes
@reactive.effect
@reactive.event(input.model)
async def _():
    await chat.clear_messages()
