from langchain_openai import ChatOpenAI

from shiny.express import ui

ui.page_opts(title="Hello dark mode!", fillable=True, fillable_mobile=True)

with ui.sidebar(open="closed", position="right", width="100px"):
    ui.tags.label("Dark mode", ui.input_dark_mode(mode="dark"))

chat = ui.Chat(id="chat")
chat.ui()

# Create the LLM client (assumes OPENAI_API_KEY is set in the environment)
llm = ChatOpenAI()


@chat.on_user_submit
async def _():
    stream = llm.astream(chat.get_messages())
    await chat.append_message_stream(stream)
