# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by OpenAI's GPT-4o model.
# To run it, you'll need OpenAI API key.
# To get setup, follow the instructions at https://platform.openai.com/docs/quickstart
# ------------------------------------------------------------------------------------
import os

from openai import AsyncOpenAI

from shiny.express import ui

# Although you can set the API key here, it's recommended to put it in an .env file
# and load it with `dotenv` so your key isn't exposed with your code:
# from dotenv import load_dotenv
# _ = load_dotenv()
llm = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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
    messages = chat.messages()
    # Create a response message stream
    response = await llm.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True,
    )
    # Append the response stream into the chat
    await chat.append_message_stream(response)
