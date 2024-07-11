# -----------------------------------------------------------------------------
# An example of placing a Shiny Chat instance in a sidebar (and having it fill the sidebar).
# To run it, you'll need an OpenAI API key.
# To get one, follow the instructions at https://platform.openai.com/docs/quickstart
# -----------------------------------------------------------------------------
import os

from langchain_openai import ChatOpenAI

from shiny.express import ui

# Provide your API key here (or set the environment variable)
llm = ChatOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # type: ignore
)

# Set some Shiny page options
ui.page_opts(
    title="Hello Sidebar Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create a chat instance, with an initial message
chat = ui.Chat(
    id="chat",
    messages=[
        {"content": "Hello! How can I help you today?", "role": "assistant"},
    ],
)

# Display the chat in a sidebar
with ui.sidebar(width=300, style="height:100%", position="right"):
    chat.ui(height="100%")


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _():
    # Get messages currently in the chat
    messages = chat.messages(format="langchain")
    # Create a response message stream
    response = llm.astream(messages)
    # Append the response stream into the chat
    await chat.append_message_stream(response)


"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
