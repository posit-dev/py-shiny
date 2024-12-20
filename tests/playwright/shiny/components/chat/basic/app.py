from shiny.express import render, ui

# Set some Shiny page options
ui.page_opts(title="Hello Chat")

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
async def handle_user_input(user_input: str):
    await chat.append_message(f"You said: {user_input}")


"Message state:"


@render.code
def message_state():
    return str(chat.messages())
