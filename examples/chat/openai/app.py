# pyright: basic
import tiktoken
from openai import AsyncOpenAI

from shiny.express import ui

ui.page_opts(
    title="Hello OpenAI Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create a chat instance, with an initial message
chat = ui.Chat(
    id="chat",
    encoding=tiktoken.encoding_for_model("gpt-4o"),
    messages=[
        {"content": "Hello! How can I help you today?", "role": "assistant"},
    ],
    # assistant_response_transformer=lambda x: HTML(f"<h1>{x}</h1"),
)

# Display the chat
chat.ui()


# Create the LLM client (assumes OPENAI_API_KEY is set in the environment)
client = AsyncOpenAI()


# on user submit, generate and append a response
@chat.on_user_submit
async def _():
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=chat.get_messages(),
        stream=True,
    )
    await chat.append_message_stream(response)
