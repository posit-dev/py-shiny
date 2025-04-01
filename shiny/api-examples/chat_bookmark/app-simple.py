from shiny.express import ui

# Set some Shiny page options
ui.page_opts(
    title="Hello Shiny Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create a welcome message
welcome = """
Hi! This is a simple Shiny `Chat` UI. Enter a message below and I will
simply repeat it back to you.

To learn more about chatbots and how to build them with Shiny, check out
[the documentation](https://shiny.posit.co/py/docs/genai-chatbots.html).
"""

# Create a chat instance
chat = ui.Chat(
    id="chat",
    messages=[welcome],
)

# Display it
chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    # Append a response to the chat
    await chat.append_message(f"You said: {user_input}")


raise RuntimeError("TODO barret make custom class here!")

chat.enable_bookmarking(
    chat_client,
    bookmark_on="response",
    # ONLY for ChatExpress.
    # For shiny-core `ui.Chat()``, use the `App(bookmark_store=)` directly
    bookmark_store="url",
)


# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by OpenAI.
# ------------------------------------------------------------------------------------

import requests
from chatlas import ChatOpenAI, Turn
from chatlas._content import Content
from dotenv import load_dotenv

from shiny import reactive
from shiny.bookmark import BookmarkState
from shiny.express import app_opts, session, ui
from shiny.types import MISSING

with ui.hold():
    load_dotenv()

chat_client = ChatOpenAI(model="gpt-4o-mini")


# Set some Shiny page options
ui.page_opts(
    fillable=True,
    fillable_mobile=True,
)

# Create and display a Shiny chat component
chat = ui.Chat(
    id="chat",
)
chat.ui(messages=["Hello! Would you like to know the weather today?"])
