from langchain_openai import ChatOpenAI

from shiny import App, ui

app_ui = ui.page_fillable(
    ui.panel_title("Hello OpenAI Chat"), ui.chat_ui("chat"), fillable_mobile=True
)


def server(input, output, session):
    chat = ui.Chat(id="chat")

    # Create the LLM client (assumes OPENAI_API_KEY is set in the environment)
    llm = ChatOpenAI()

    @chat.on_user_submit
    async def _():
        response = llm.astream(chat.get_messages())
        await chat.append_message_stream(response)


app = App(app_ui, server)
