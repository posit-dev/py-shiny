from shiny.express import render, ui

# Set some Shiny page options
ui.page_opts(title="Hello Chat")

# Create a chat instance, with an initial message
chat = ui.Chat(id="chat")

# Display the chat
chat.ui()


@chat.transform_assistant_response
async def transform(content: str) -> str:
    if content == "return HTML":
        return ui.HTML(f"<b>Transformed response</b>: {content}")
    else:
        return f"Transformed response: `{content}`"


@chat.on_user_submit
async def _():
    user = chat.get_user_input()
    await chat.append_message(user)


"Message state:"


@render.code
def message_state():
    return str(chat.get_messages())
