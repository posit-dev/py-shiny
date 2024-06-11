import ollama

from shiny.express import ui

ui.page_opts(
    title="Hello Ollama Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create and display empty chat
chat = ui.Chat(id="chat")
chat.ui()


# on user submit, generate and append a response
@chat.on_user_submit
async def _():
    response = ollama.chat(
        model="llama3",
        messages=chat.get_messages(),
        stream=True,
    )
    await chat.append_message_stream(response)
