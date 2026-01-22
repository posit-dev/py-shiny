from shiny import App, ui

app_ui = ui.page_fillable(
    ui.panel_title("Hello Shiny Chat"),
    ui.chat_ui("chat"),
    ui.chat_ui(
        "chat",
        messages=[
            """
Hi! This is a simple Shiny `Chat` UI. Enter a message below and I will
simply repeat it back to you.

To learn more about chatbots and how to build them with Shiny, check out
[the documentation](https://shiny.posit.co/py/docs/genai-chatbots.html).
"""
        ],
    ),
    fillable_mobile=True,
)


def server(input, output, session):
    chat = ui.Chat(id="chat")

    # Define a callback to run when the user submits a message
    @chat.on_user_submit
    async def handle_user_input(user_input: str):
        # Append a response to the chat
        await chat.append_message(f"You said: {user_input}")


app = App(app_ui, server)
