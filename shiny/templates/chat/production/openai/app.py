# ------------------------------------------------------------------------------------
# When putting a Chat into production, there are at least a couple additional
# considerations to keep in mind:
#  - Token Limits: LLMs have (varying) limits on how many tokens can be included in
#    a single request and response. To accurately respect these limits, you'll want
#    to find the revelant limits and tokenizer for the model you're using, and inform
#    Chat about them.
#  - Reproducibility: Consider pinning a snapshot of the LLM model to ensure that the
#    same model is used each time the app is run.
#
# See the MODEL_CONFIG dictionary below for an example of how to set these values for
# OpenAI's GPT-4o model.
# ------------------------------------------------------------------------------------
import os

import tiktoken
from app_utils import load_dotenv
from chatlas import Chat, ChatOpenAI

from shiny.express import ui

MODEL_CONFIG = {
    "name": "gpt-4o-2024-08-06",
    "context_window": 128000,
    "max_tokens": 16000,
}

load_dotenv()
chat_model = ChatOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model=MODEL_CONFIG["name"],
)


ui.page_opts(
    title="Hello OpenAI Chat",
    fillable=True,
    fillable_mobile=True,
)

chat = ui.Chat(
    id="chat",
    messages=["Hello! How can I help you today?"],
)

chat.ui()


@chat.on_user_submit
async def handle_user_input(user_input):
    response = await chat_model.stream_async(user_input)
    await chat.append_message_stream(response)


tokenizer = tiktoken.encoding_for_model(MODEL_CONFIG["name"])
