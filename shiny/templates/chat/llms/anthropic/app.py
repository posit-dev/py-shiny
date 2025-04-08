# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by Anthropic's Claude model.
# ------------------------------------------------------------------------------------
import os

from app_utils import load_dotenv
from chatlas import ChatAnthropic

from shiny.express import ui

# ChatAnthropic() requires an API key from Anthropic.
# See the docs for more information on how to obtain one.
# https://posit-dev.github.io/chatlas/reference/ChatAnthropic.html
load_dotenv()
chat_client = ChatAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    model="claude-3-7-sonnet-latest",
    system_prompt="You are a helpful assistant.",
)


# Set some Shiny page options
ui.page_opts(
    title="Hello Anthropic Claude Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create and display a Shiny chat component
chat = ui.Chat(
    id="chat",
    messages=["Hello! How can I help you today?"],
)
chat.ui()

# Store chat state in the url when an "assistant" response occurs
chat.enable_bookmarking(chat_client, bookmark_store="url")


# Generate a response when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    response = await chat_client.stream_async(user_input)
    await chat.append_message_stream(response)
