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
# Anthropic's Claude 3.5 Sonnet model.
# https://docs.anthropic.com/en/docs/about-claude/models#model-comparison-table
# ------------------------------------------------------------------------------------
import os

from app_utils import load_dotenv
from chatlas import Chat, ChatAnthropic

from shiny.express import ui

MODEL_CONFIG = {
    "name": "claude-3-5-sonnet-20240620",
    "context_window": 200000,
    "max_tokens": 8192,
}

load_dotenv()
chat_model = ChatAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    model=MODEL_CONFIG["name"],
    max_tokens=MODEL_CONFIG["max_tokens"],
    system_prompt="You are a helpful assistant.",
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


def trim_chat_turns(turns, max_turns=5):
    return turns[-max_turns:]
