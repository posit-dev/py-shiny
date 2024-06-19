from langchain_openai import ChatOpenAI

from shiny.express import ui

ui.page_opts(
    title="Hello LangChain Chat Models",
    fillable=True,
    fillable_mobile=True,
)

# Create and display an empty chat UI
chat = ui.Chat(id="chat")
chat.ui()

# Create the chat model
llm = ChatOpenAI()

# --------------------------------------------------------------------
# To use a different model, replace the line above with any model that subclasses
# langchain's BaseChatModel. For example, to use Anthropic:
# from langchain_anthropic import ChatAnthropic
# llm = ChatAnthropic(model="claude-3-sonnet-20240229")
# For more information, see the langchain documentation.
# https://python.langchain.com/v0.1/docs/modules/model_io/chat/quick_start/
# --------------------------------------------------------------------


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _():
    # Get all the messages currently in the chat
    messages = chat.get_messages()
    # Create an async generator from the messages
    stream = llm.astream(messages)
    # Append the response stream into the chat
    await chat.append_message_stream(stream)
