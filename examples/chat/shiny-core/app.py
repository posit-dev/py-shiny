# ------------------------------------------------------------------------
# A basic Shiny Chat in Shiny Core example (most other examples use Shiny Express).
# To run it, you'll need an OpenAI API key.
# To get one, follow the instructions at https://platform.openai.com/docs/quickstart
# ------------------------------------------------------------------------
import os

from langchain_openai import ChatOpenAI

from shiny import App, ui

# Provide your API key here (or set the environment variable)
llm = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app_ui = ui.page_fillable(
    ui.panel_title("Hello OpenAI Chat"),
    ui.chat_ui("chat"),
    fillable_mobile=True,
)


def server(input, output, session):
    chat = ui.Chat(id="chat")

    # Define a callback to run when the user submits a message
    @chat.on_user_submit
    async def _():
        # Get messages currently in the chat
        messages = chat.get_messages()
        # Create a response message stream
        response = llm.astream(messages)
        # Append the response stream into the chat
        await chat.append_message_stream(response)


app = App(app_ui, server)
