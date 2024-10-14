# --------------------------------------------------------------------------------
# This example demonstrates Shiny Chat's dark mode capability.
# To run it, you'll need an OpenAI API key.
# To get one, follow the instructions at https://platform.openai.com/docs/quickstart
# --------------------------------------------------------------------------------
import os

from langchain_openai import ChatOpenAI

from shiny.express import ui

# Provide your API key here (or set the environment variable)
llm = ChatOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # type: ignore
)

# Set some Shiny page options
ui.page_opts(
    title="Hello dark mode!",
    fillable=True,
    fillable_mobile=True,
)

# Create a sidebar to select the dark mode
with ui.sidebar(open="closed", position="right", width="100px"):
    ui.tags.label("Dark mode", ui.input_dark_mode(mode="dark"))

# Create and display an empty chat UI
chat = ui.Chat(id="chat")
chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _():
    # Get messages currently in the chat
    messages = chat.messages(format="langchain")
    # Create a response message stream
    stream = llm.astream(messages)
    # Append the response stream into the chat
    await chat.append_message_stream(stream)
