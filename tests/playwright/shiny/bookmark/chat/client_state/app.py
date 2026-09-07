from typing import cast

from shiny.express import ui
from shiny.types import Jsonifiable, JsonifiableDict

# Set some Shiny page options
ui.page_opts(
    title="Hello Shiny Chat",
    fillable=True,
    fillable_mobile=True,
)


# Create a chat instance. The startup message is a `greeting=`: shinychat 0.7.0
# deprecated `Chat(messages=)` and raises unless `history=False` is also passed.
# `enable_bookmarking()` bookmarks and restores the greeting content, so this
# still covers the round-trip.
chat = ui.Chat(
    id="chat",
    greeting="""Welcome!""",
)

# Display it
chat.ui()


class RepeaterClient:
    """
    A simple chat client repeater that echoes back the user's input.
    """

    def __init__(self, *, messages: list[str]):
        self.messages = messages

    def append_message(self, message: str) -> str:
        msg = f"Repeater: {message}"
        self.messages.append(msg)
        return msg

    async def get_state(self) -> Jsonifiable:
        """
        Get the current state of the chat client.
        """
        return cast(JsonifiableDict, {"messages": self.messages})

    async def set_state(self, state: Jsonifiable) -> None:
        """ "
        Set the state of the chat client.
        """
        assert isinstance(state, dict)
        assert "messages" in state
        assert isinstance(state["messages"], list)
        assert all(isinstance(message, str) for message in state["messages"])
        self.messages = cast(list[str], state["messages"])


chat_client = RepeaterClient(messages=[])

chat.enable_bookmarking(chat_client, bookmark_store="url")


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    msg = chat_client.append_message(user_input)
    # Append a response to the chat
    await chat.append_message(msg)
