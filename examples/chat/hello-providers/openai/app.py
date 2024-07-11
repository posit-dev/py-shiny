# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by OpenAI's GPT-4o model.
# To run it, you'll need OpenAI API key.
# To get setup, follow the instructions at https://platform.openai.com/docs/quickstart
# ------------------------------------------------------------------------------------
import os

from app_utils import load_dotenv
from openai import AsyncOpenAI

from shiny.express import ui

# Either explicitly set the OPENAI_API_KEY environment variable before launching the
# app, or set them in a file named `.env`. The `python-dotenv` package will load `.env`
# as environment variables which can later be read by `os.getenv()`.
load_dotenv()
llm = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Set some Shiny page options
ui.page_opts(
    title="Hello OpenAI Chat",
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

# Display the chat
chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _():
    # Get messages currently in the chat
    messages = chat.messages(format="openai")
    # Create a response message stream
    response = await llm.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True,
    )
    # Append the response stream into the chat
    await chat.append_message_stream(response)
