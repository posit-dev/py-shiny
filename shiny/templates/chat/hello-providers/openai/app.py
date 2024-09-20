import os

from app_utils import load_dotenv

from shiny.express import ui
from shiny.ui._chat_client_openai import OpenAIClient

ui.page_opts(
    title="Hello OpenAI Chat",
    fillable=True,
    fillable_mobile=True,
)

load_dotenv()
llm = OpenAIClient(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o",
)

chat = ui.Chat(
    id="chat",
    messages=["Hello! How can I help you today?"],
)

chat.ui()


@chat.on_user_submit
async def _(input):
    response = llm.generate_response(input, stream=False)
    await chat.append_message(response)
