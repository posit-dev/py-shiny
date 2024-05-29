import ollama

from shiny.express import ui

ui.page_opts(
    title="Hello Ollama Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create a chat instance
chat = ui.Chat(id="chat")

# Display the chat
chat


# on user submit, generate and append a response
@chat.on_user_submit
async def _():
    response = ollama.chat(
        model="llama3",
        messages=chat.messages(),
        stream=True,
    )
    await chat.append_message_stream(response)
