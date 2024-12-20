# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by OpenAI running on Azure.
# ------------------------------------------------------------------------------------
import os

from app_utils import load_dotenv
from chatlas import ChatAzureOpenAI

from shiny.express import ui

# ChatAzureOpenAI() requires an API key from Azure OpenAI.
# See the docs for more information on how to obtain one.
# https://posit-dev.github.io/chatlas/reference/ChatAzureOpenAI.html
load_dotenv()
chat_model = ChatAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    endpoint="https://my-endpoint.openai.azure.com",
    deployment_id="gpt-4o-mini",
    api_version="2024-08-01-preview",
)

# Set some Shiny page options
ui.page_opts(
    title="Hello Azure OpenAI Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create a chat instance, with an initial message
chat = ui.Chat(
    id="chat",
    messages=["Hello! How can I help you today?"],
)
chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    response = chat_model.stream(user_input)
    await chat.append_message_stream(response)
