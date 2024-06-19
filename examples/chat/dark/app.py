from langchain_openai import ChatOpenAI

from shiny.express import ui

ui.page_opts(title="Hello dark mode!", fillable=True, fillable_mobile=True)

with ui.sidebar(open="closed", position="right", width="100px"):
    ui.tags.label("Dark mode", ui.input_dark_mode())


# Create and display an empty chat UI
chat = ui.Chat(id="chat")
chat.ui()

# Create the chat model
llm = ChatOpenAI()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _():
    # Get all the messages currently in the chat
    messages = chat.get_messages()
    # Create an async generator from the messages
    stream = llm.astream(messages)
    # Append the response stream into the chat
    await chat.append_message_stream(stream)
