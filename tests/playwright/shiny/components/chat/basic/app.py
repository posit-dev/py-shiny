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
async def _():
    user_msg = chat.user_input()
    await chat.append_message(f"You said: {user_msg}")


"Message state:"


@render.code
def message_state():
    return str(chat.messages())
