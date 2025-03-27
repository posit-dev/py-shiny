from shiny.express import ui

# Set some Shiny page options
ui.page_opts(
    title="Hello Shiny Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create a welcome message
welcome = """
Hi! This is a simple Shiny `Chat` UI. Enter a message below and I will
simply repeat it back to you.

To learn more about chatbots and how to build them with Shiny, check out
[the documentation](https://shiny.posit.co/py/docs/genai-chatbots.html).
"""

# Create a chat instance
chat = ui.Chat(
    id="chat",
    messages=[welcome],
)

# Display it
chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    # Append a response to the chat
    await chat.append_message(f"You said: {user_input}")
