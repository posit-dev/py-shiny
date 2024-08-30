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
# See the MODEL_INFO dictionary below for an example of how to set these values for
# OpenAI's GPT-4o model.
# ------------------------------------------------------------------------------------
import os

import tiktoken
from app_utils import load_dotenv
from openai import AsyncOpenAI

from shiny.express import ui

load_dotenv()
llm = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


MODEL_INFO = {
    "name": "gpt-4o-2024-08-06",
    "tokenizer": tiktoken.encoding_for_model("gpt-4o-2024-08-06"),
    "token_limits": (128000, 16000),
}


ui.page_opts(
    title="Hello OpenAI Chat",
    fillable=True,
    fillable_mobile=True,
)

chat = ui.Chat(
    id="chat",
    messages=[
        {"content": "Hello! How can I help you today?", "role": "assistant"},
    ],
    tokenizer=MODEL_INFO["tokenizer"],
)

chat.ui()


@chat.on_user_submit
async def _():
    messages = chat.messages(format="openai", token_limits=MODEL_INFO["token_limits"])
    response = await llm.chat.completions.create(
        model=MODEL_INFO["name"], messages=messages, stream=True
    )
    await chat.append_message_stream(response)
