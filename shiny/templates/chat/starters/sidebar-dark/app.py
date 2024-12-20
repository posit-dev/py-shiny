# --------------------------------------------------------------------------------
# This example demonstrates Shiny Chat's dark mode capability.
# --------------------------------------------------------------------------------

from shiny.express import ui

# Page options with a dark mode toggle
ui.page_opts(
    title=ui.tags.div(
        "Hello Dark mode",
        ui.input_dark_mode(mode="dark"),
        class_="d-flex justify-content-between w-100",
    ),
    fillable=True,
    fillable_mobile=True,
)

# An empty, closed, sidebar
with ui.sidebar(width=300, style="height:100%", position="right"):
    chat = ui.Chat(id="chat", messages=["Welcome to the dark side!"])
    chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    await chat.append_message_stream(f"You said: {user_input}")


"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
