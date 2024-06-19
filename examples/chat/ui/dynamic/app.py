from langchain_openai import ChatOpenAI

from shiny.express import input, render, ui

ui.input_select("model", "Model", choices=["gpt-4o", "gpt-3.5-turbo"])


@render.express
def chat_ui():

    chat = ui.Chat(
        id="chat",
        messages=[
            {
                "content": f"Hi! I'm a {input.model()} model. How can I help you today?",
                "role": "assistant",
            }
        ],
    )

    chat.ui()

    # Create the LLM client (assumes OPENAI_API_KEY is set in the environment)
    llm = ChatOpenAI(model=input.model())

    @chat.on_user_submit
    async def _():
        response = llm.astream(chat.get_messages())
        await chat.append_message_stream(response)
