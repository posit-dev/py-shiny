# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by OpenAI's GPT-4o model.
# To run it, you'll need OpenAI API key.
# To get setup, follow the instructions at https://platform.openai.com/docs/quickstart
# ------------------------------------------------------------------------------------
import os

from app_utils import load_dotenv
from chatlas import OpenAIChat

from shiny.express import ui

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
async def _(message):
    response = llm.response_generator(message)
    await chat.append_message_stream(response)


# Create a chatlas OpenAI chat model
#
# Either explicitly set the OPENAI_API_KEY environment variable before launching the
# app, or set them in a file named `.env`. The `python-dotenv` package will load `.env`
# as environment variables which can later be read by `os.getenv()`.
load_dotenv()
llm = OpenAIChat(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o",
    system_prompt="You are a helpful assistant.",
)
