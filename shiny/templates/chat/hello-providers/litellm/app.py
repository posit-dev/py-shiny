# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by OpenAI's GPT-4o model using the `litellm` library.
# To run it, you'll need OpenAI API key.
# To get setup, follow the instructions at https://platform.openai.com/docs/quickstart
# ------------------------------------------------------------------------------------
import litellm
from app_utils import load_dotenv

from shiny.express import ui

# Load a .env file (if it exists) to get the OpenAI API key
load_dotenv()

chat = ui.Chat(id="chat")
chat.ui()


@chat.on_user_submit
async def _():
    messages = chat.messages()
    response = await litellm.acompletion(model="gpt-4o", messages=messages, stream=True)
    await chat.append_message_stream(response)
