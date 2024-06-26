# ------------------------------------------------------------------------------------
# A Shiny Chat example showing how to use different language models via LangChain.
# To run it with all the different providers/models, you'll need API keys for each.
# Namely, OPENAI_API_KEY, ANTHROPIC_API_KEY, and GOOGLE_API_KEY.
# To see how to get these keys, see the relevant basic examples.
# (i.e., ../basic/openai/app.py, ../basic/anthropic/app.py, ../basic/gemini/app.py)
# ------------------------------------------------------------------------------------

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_vertexai import VertexAI
from langchain_openai import ChatOpenAI

from shiny.express import input, render, ui

models = {
    "openai": ["gpt-4o", "gpt-3.5-turbo"],
    "claude": [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
    "google": ["gemini-1.5-pro-latest"],
}

model_choices = {}
for key, value in models.items():
    model_choices[key] = dict(zip(value, value))

ui.page_opts(
    title="Shiny Chat Playground",
    fillable=True,
    fillable_mobile=True,
)

with ui.sidebar(position="right"):
    ui.input_select("model", "Model", choices=model_choices)
    ui.input_select(
        "system_actor",
        "Response style",
        choices=["Chuck Norris", "Darth Vader", "Yoda", "Gandalf", "Sherlock Holmes"],
    )
    ui.input_switch("stream", "Stream", value=False)
    ui.input_slider("temperature", "Temperature", min=0, max=2, step=0.1, value=1)
    ui.input_slider("max_tokens", "Max Tokens", min=1, max=4096, step=1, value=100)


@render.express(fill=True, fillable=True)
def chat_ui():
    chat = ui.Chat(id="chat")

    model_params = {
        "model": input.model(),
        "temperature": input.temperature(),
        "max_tokens": input.max_tokens(),
    }

    if input.model() in models["openai"]:
        llm = ChatOpenAI(**model_params)
    elif input.model() in models["claude"]:
        llm = ChatAnthropic(**model_params)
    elif input.model() in models["google"]:
        llm = VertexAI(**model_params)
    else:
        raise ValueError(f"Invalid model: {input.model()}")

    system_message = SystemMessage(
        f"You are a helpful AI assistant. Provide answers in the style of {input.system_actor()}."
    )

    @chat.on_user_submit
    async def _():

        # Transform ChatMessage(s) into langchain's message types
        messages = [system_message]
        for message in chat.get_messages():
            role = message["role"]
            content = message["content"]
            if role == "user":
                messages.append(HumanMessage(content))
            elif role == "assistant":
                messages.append(AIMessage(content))

        if input.stream():
            response = llm.astream(messages)
            await chat.append_message_stream(response)
        else:
            response = await llm.ainvoke(messages)
            await chat.append_message(response)

    chat.ui()
