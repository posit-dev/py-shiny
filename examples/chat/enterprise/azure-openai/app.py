# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by OpenAI running on Azure.
# To run it, you'll need OpenAI API key.
# To get setup, follow the instructions at https://learn.microsoft.com/en-us/azure/ai-services/openai/quickstart?tabs=command-line%2Cpython-new&pivots=programming-language-python#create-a-new-python-application
# ------------------------------------------------------------------------------------
import os

from app_utils import load_dotenv
from openai import AzureOpenAI

from shiny.express import ui

# Either explicitly set the AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment
# variables before launching the app, or set them in a file named `.env`. The
# `python-dotenv` package will load `.env` as environment variables which can later be
# read by `os.getenv()`.
load_dotenv()

llm = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),  # type: ignore
)

deployment_name = "REPLACE_WITH_YOUR_DEPLOYMENT_NAME"

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
    response = llm.chat.completions.create(
        model=deployment_name,
        messages=messages,
        stream=True,
    )
    # Append the response stream into the chat
    await chat.append_message_stream(response)
