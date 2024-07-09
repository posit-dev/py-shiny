# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by OpenAI via LangChain.
# To run it, you'll need OpenAI API key.
# To get one, follow the instructions at https://platform.openai.com/docs/quickstart
# To use other providers/models via LangChain, see https://python.langchain.com/v0.1/docs/modules/model_io/chat/quick_start/
# ------------------------------------------------------------------------------------
import os

from langchain_openai import ChatOpenAI

from shiny.express import ui

# Either set the OPENAI_API_KEY environment variable before launching the app, or set it
# a .env file and load it with `python-dotenv`. Uncomment the lines below to use dotenv.
# from pathlib import Path
# from dotenv import load_dotenv
# _ = load_dotenv(Path(__file__).parent / ".env")
llm = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Set some Shiny page options
ui.page_opts(
    title="Hello LangChain Chat Models",
    fillable=True,
    fillable_mobile=True,
)

# Create and display an empty chat UI
chat = ui.Chat(id="chat")
chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _():
    # Get messages currently in the chat
    messages = chat.messages()
    # Create a response message stream
    response = llm.astream(messages)
    # Append the response stream into the chat
    await chat.append_message_stream(response)
