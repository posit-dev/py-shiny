from langchain_openai import OpenAI

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

    llm = OpenAI(model=input.model())

    @chat.on_user_submit
    async def _():
        response = llm.astream(chat.get_messages())
        await chat.append_message_stream(response)
