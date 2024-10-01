# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by Ollama.
# To run it, you'll need an Ollama server running locally.
# To download and run the server, see https://github.com/ollama/ollama
# To install the Ollama Python client, see https://github.com/ollama/ollama-python
# ------------------------------------------------------------------------------------

from chatlas import OllamaChat

from shiny.express import ui

# Set some Shiny page options
ui.page_opts(
    title="Hello Ollama Chat",
    fillable=True,
    fillable_mobile=True,
)

# Assumes you're running an Ollama server (with llama3 available) locally
llm = OllamaChat(model="llama3.1")

# Create and display empty chat
chat = ui.Chat(
    id="chat",
    messages=["Hello! How can I help you today?"],
)
chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _(input):
    response = llm.response_generator(input)
    await chat.append_message_stream(response)
