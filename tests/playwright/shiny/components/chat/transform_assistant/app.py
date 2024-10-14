from typing import Union

from shiny.express import render, ui

# Set some Shiny page options
ui.page_opts(title="Hello Chat")

# Create a chat instance, with an initial message
chat = ui.Chat(id="chat")

# Display the chat
chat.ui()


# TODO: test with append_message_stream() as well
@chat.transform_assistant_response
def transform(content: str) -> Union[str, ui.HTML]:
    if content == "return HTML":
        return ui.HTML(f"<b>Transformed response</b>: {content}")
    else:
        return f"Transformed response: `{content}`"


@chat.on_user_submit
async def _():
    user = chat.user_input()
    await chat.append_message(user)


"chat.messages():"


@render.code
def message_state():
    return str(chat.messages())


"chat.messages(transform_assistant=True):"


@render.code
def message_state2():
    return str(chat.messages(transform_assistant=True))
