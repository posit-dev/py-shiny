# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by Anthropic's Claude model.
# To run it, you'll need an Anthropic API key.
# To get one, follow the instructions at https://docs.anthropic.com/en/api/getting-started
# ------------------------------------------------------------------------------------
import os

from anthropic import AsyncAnthropic
from app_utils import load_dotenv

from shiny.express import ui

# Either explicitly set the ANTHROPIC_API_KEY environment variable before launching the
# app, or set them in a file named `.env`. The `python-dotenv` package will load `.env`
# as environment variables which can later be read by `os.getenv()`.
load_dotenv()
llm = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Set some Shiny page options
ui.page_opts(
    title="Hello Anthropic Claude Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create and display empty chat
chat = ui.Chat(id="chat")
chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _():
    # Get messages currently in the chat
    messages = chat.messages(format="anthropic")
    # Create a response message stream
    response = await llm.messages.create(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        stream=True,
        max_tokens=1000,
    )
    # Append the response stream into the chat
    await chat.append_message_stream(response)
