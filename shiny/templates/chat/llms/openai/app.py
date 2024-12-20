# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by OpenAI.
# ------------------------------------------------------------------------------------
import os

from app_utils import load_dotenv
from chatlas import ChatOpenAI

from shiny.express import ui

# ChatOpenAI() requires an API key from OpenAI.
# See the docs for more information on how to obtain one.
# https://posit-dev.github.io/chatlas/reference/ChatOpenAI.html
load_dotenv()
chat_model = ChatOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o",
    system_prompt="You are a helpful assistant.",
)


# Set some Shiny page options
ui.page_opts(
    title="Hello OpenAI Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create and display a Shiny chat component
chat = ui.Chat(
    id="chat",
    messages=["Hello! How can I help you today?"],
)
chat.ui()


# Generate a response when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    response = chat_model.stream(user_input)
    await chat.append_message_stream(response)
