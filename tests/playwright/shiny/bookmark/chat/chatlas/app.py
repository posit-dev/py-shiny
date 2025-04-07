import chatlas

from shiny.express import ui

# Set some Shiny page options
ui.page_opts(
    title="Hello Shiny Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create a chat instance
init_messages = ["""Welcome!"""]
chat = ui.Chat(
    id="chat",
    messages=init_messages,
)

# Display it
chat.ui()

# Goal: Test that chatlas is serializied and deserialized correctly.
#
# Use ChatOpenAI as it does not need credentials until submission to the server.
# However, if we use `.set_turns()` and `.get_turns()`, a submission is never made to the server... therefore we don't need credentials.
chat_client = chatlas.ChatOpenAI(  # pyright: ignore[reportUnknownMemberType]
    turns=[],
    api_key="<not_utilized>",
)
chat.enable_bookmarking(chat_client, bookmark_store="url")


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    mock_msg = f"You said to OpenAI: {user_input}"
    chat_client.set_turns(  # pyright: ignore[reportUnknownMemberType]
        [
            *chat_client.get_turns(),
            chatlas.Turn(role="user", contents=user_input),
            chatlas.Turn(role="assistant", contents=mock_msg),
        ]
    )

    # Append a response to the chat
    await chat.append_message(mock_msg)
