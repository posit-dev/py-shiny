from langchain_openai import ChatOpenAI

from shiny.express import ui

ui.page_opts(
    title="Hello Sidebar Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create a chat instance, with an initial message
chat = ui.Chat(
    id="chat",
    messages=[
        {"content": "Hello! How can I help you today?", "role": "assistant"},
    ],
)

# Display the chat in a sidebar
with ui.sidebar(width=300, style="height:100%", position="right"):
    chat.ui(height="100%")


# Create the LLM client (assumes OPENAI_API_KEY is set in the environment)
llm = ChatOpenAI()


# on user submit, generate and append a response
@chat.on_user_submit
async def _():
    response = llm.astream(chat.get_messages())
    await chat.append_message_stream(response)


"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
