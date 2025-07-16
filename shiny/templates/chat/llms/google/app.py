# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by Google's Gemini model.
# ------------------------------------------------------------------------------------
import os

from app_utils import load_dotenv
from chatlas import ChatGoogle

from shiny.express import ui

# ChatGoogle() requires an API key from Google.
# See the docs for more information on how to obtain one.
# https://posit-dev.github.io/chatlas/reference/ChatGoogle.html
load_dotenv()
chat_client = ChatGoogle(
    api_key=os.environ.get("GOOGLE_API_KEY"),
    system_prompt="You are a helpful assistant.",
    model="gemini-2.0-flash",
)

# Set some Shiny page options
ui.page_opts(
    title="Hello Google Gemini Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create and display empty chat
chat = ui.Chat(id="chat")
chat.ui()

# Store chat state in the url when an "assistant" response occurs
chat.enable_bookmarking(chat_client, bookmark_store="url")


# Generate a response when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    response = await chat_client.stream_async(user_input)
    await chat.append_message_stream(response)
