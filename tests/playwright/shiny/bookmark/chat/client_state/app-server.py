import atexit
import os
import shutil
import tempfile
from pathlib import Path
from typing import cast

from shiny.bookmark import set_global_restore_dir_fn, set_global_save_dir_fn
from shiny.express import ui
from shiny.types import Jsonifiable, JsonifiableDict

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


chat_client = RepeaterClient(messages=init_messages)


# Note:
# This is a "temp" directory that is only used for testing and is cleaned up when the
# app process exits. This should NOT be standard behavior of a hosting environment.
# Instead, it should have a persistent directory that can be restored over time.
# NOTE: keyed on the process id, not `mkdtemp()`. Express re-executes this module
# for every session, so a fresh temp directory per run would leave each restore
# looking in an empty directory. The pid is stable across the sessions of one app
# process and unique between concurrent test runs.
bookmark_dir = Path(tempfile.gettempdir()) / f"shiny-chat-bookmarks-{os.getpid()}"
bookmark_dir.mkdir(parents=True, exist_ok=True)


# NOTE: registered via a decorated `def`, not a bare `atexit.register(...)` call.
# In Express mode a top-level expression becomes UI, and `atexit.register()`
# returns the function it registered, which is not a valid tag item.
@atexit.register
def _cleanup_bookmark_dir() -> None:
    shutil.rmtree(bookmark_dir, ignore_errors=True)


# NOTE: applied as decorators rather than called as bare top-level expressions.
# These functions return the function they were given, and in Express mode a
# top-level expression becomes UI -- a function is not a valid tag item.
@set_global_restore_dir_fn
def restore_bookmark_dir(id: str) -> Path:
    return bookmark_dir / id


@set_global_save_dir_fn
def save_bookmark_dir(id: str) -> Path:
    save_dir = bookmark_dir / id
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir


# Same app as `app.py`, but with server-side bookmark storage. `"server"` exercises
# the `_state_id_` restore path, where a plain page load has no `_state_id_` at all --
# `ui.Chat` still has to render its initial messages in that case.
chat.enable_bookmarking(chat_client, bookmark_store="server")


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    msg = chat_client.append_message(user_input)
    # Append a response to the chat
    await chat.append_message(msg)
