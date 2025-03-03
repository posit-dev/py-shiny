from shiny import App, ui

app_ui = ui.page_fillable(
    ui.panel_title("Hello Shiny Chat"),
    ui.chat_ui("chat"),
    fillable_mobile=True,
)

# Create a welcome message
welcome = """
Hi! This is a simple Shiny `Chat` UI. Enter a message below and I will
simply repeat it back to you. For more examples, see this
[folder of examples](https://github.com/posit-dev/py-shiny/tree/main/shiny/templates/chat).
"""


def server(input, output, session):
    chat = ui.Chat(id="chat", messages=[welcome])

    # Define a callback to run when the user submits a message
    @chat.on_user_submit
    async def handle_user_input(user_input: str):
        # Append a response to the chat
        await chat.append_message(f"You said: {user_input}")


app = App(app_ui, server)
