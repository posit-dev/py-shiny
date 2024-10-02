# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by Anthropic's Claude model.
# To run it, you'll need an Anthropic API key.
# To get one, follow the instructions at https://docs.anthropic.com/en/api/getting-started
# ------------------------------------------------------------------------------------
import os

from app_utils import load_dotenv
from chatlas import AnthropicChat

from shiny.express import ui

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


# Generate a response when the user submits a message
@chat.on_user_submit
async def _(message):
    response = llm.response_generator(message)
    await chat.append_message_stream(response)


# Create an Anthropic Claude chat model
#
# Either explicitly set the ANTHROPIC_API_KEY environment variable before launching the
# app, or set them in a file named `.env`. The `python-dotenv` package will load `.env`
# as environment variables which can later be read by `os.getenv()`.
load_dotenv()
llm = AnthropicChat(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    model="claude-3-5-sonnet-20240620",
    system_prompt="You are a helpful assistant.",
)
