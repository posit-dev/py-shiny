from shiny.express import ui

# Set some Shiny page options
ui.page_opts(
    title="Hello Shiny Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create a welcome message
welcome = ui.markdown(
    """
    Hi! This is a simple Shiny `Chat` UI. Enter a message below and I will
    simply repeat it back to you. For more examples, see this
    [folder of examples](https://github.com/posit-dev/py-shiny/tree/main/examples/chat).
    """
)

# Create a chat instance
chat = ui.Chat(
    id="chat",
    messages=[welcome],
)

# Display it
chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _():
    # Get the user's input
    user = chat.user_input()
    # Append a response to the chat
    await chat.append_message(f"You said: {user}")
