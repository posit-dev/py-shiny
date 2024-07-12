# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by Ollama.
# To run it, you'll need an Ollama server running locally.
# To download and run the server, see https://github.com/ollama/ollama
# To install the Ollama Python client, see https://github.com/ollama/ollama-python
# ------------------------------------------------------------------------------------

import ollama

from shiny.express import ui

# Set some Shiny page options
ui.page_opts(
    title="Hello Ollama Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create and display empty chat
chat = ui.Chat(id="chat")
chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _():
    # Get messages currently in the chat
    messages = chat.messages(format="ollama")
    # Create a response message stream
    # Assumes you've run `ollama run llama3` to start the server
    response = ollama.chat(
        model="llama3",
        messages=messages,
        stream=True,
    )
    # Append the response stream into the chat
    await chat.append_message_stream(response)
