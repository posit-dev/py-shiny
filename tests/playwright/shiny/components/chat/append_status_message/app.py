from shiny import reactive
from shiny.express import input, ui

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

with ui.card():
    ui.card_header("Status Message")

    with ui.layout_columns():
        with ui.div():
            ui.input_text(
                "content", "Message Content", "Using model <code>llama3.2</code>"
            )
            ui.input_switch("content_is_html", "Raw HTML", True)

        ui.input_radio_buttons("type", "Status type", choices=["dynamic", "static"])

    ui.input_action_button("submit", "Send status message")


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    await chat.append_message(f"You said: {user_input}")


@reactive.effect
@reactive.event(input.submit)
async def send_status_message():
    content = input.content()
    if input.content_is_html.get():
        content = ui.HTML(content)

    await chat.append_status_message(content, type=input.type())
