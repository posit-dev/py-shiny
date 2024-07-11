# -----------------------------------------------------------------------------
# A basic example of dynamically re-rendering a Shiny Chat instance with different models.
# To run it, you'll need an OpenAI API key.
# To get one, follow the instructions at https://platform.openai.com/docs/quickstart
# -----------------------------------------------------------------------------
import os

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

    llm = ChatOpenAI(
        model=input.model(),
        # Provide your API key here (or set the environment variable)
        api_key=os.environ.get("OPENAI_API_KEY"),  # type: ignore
    )

    @chat.on_user_submit
    async def _():
        messages = chat.messages(format="langchain")
        response = llm.astream(messages)
        await chat.append_message_stream(response)
