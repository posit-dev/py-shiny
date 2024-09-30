import os

from app_utils import load_dotenv
from chatlas import OpenAI

from shiny.express import ui

ui.page_opts(
    title="Hello OpenAI Chat",
    fillable=True,
    fillable_mobile=True,
)

load_dotenv()
llm = OpenAI(
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
    response = llm.response_generator(input)
    await chat.append_message_stream(response)
