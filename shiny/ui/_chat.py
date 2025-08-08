from shinychat import Chat, chat_ui
from shinychat.express import Chat as ChatExpress
from shinychat.types import ChatMessageDict

from .._docstring import add_example

__all__ = (
    "Chat",
    "ChatExpress",
    "chat_ui",
    "ChatMessageDict",
)

Chat = add_example(
    app_file="app-core.py",
    ex_dir="../shiny/api-examples/Chat",
)(Chat)

ChatExpress = add_example(
    app_file="app-express.py",
    ex_dir="../shiny/api-examples/Chat",
)(ChatExpress)

chat_ui = add_example(
    app_file="app-core.py",
    ex_dir="../shiny/api-examples/Chat",
)(chat_ui)
