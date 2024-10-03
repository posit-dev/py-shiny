from chatlas import OllamaChat

from shiny.express import ui

ui.page_opts(
    title="Tool calling with Ollama",
    fillable=True,
    fillable_mobile=True,
)


def get_current_weather(location: str, unit: str = "fahrenheit") -> int:
    if "boston" in location.lower():
        return 12 if unit == "fahrenheit" else -11
    elif "new york" in location.lower():
        return 20 if unit == "fahrenheit" else -6
    else:
        return 72 if unit == "fahrenheit" else 22


# Assumes you're running an Ollama server (with llama3 available) locally
llm = OllamaChat(
    model="llama3.1",
    tools=[get_current_weather],
)

chat = ui.Chat(
    id="chat",
    messages=["Hello! How can I help you today?"],
)

chat.ui()
chat.update_user_input(
    value="What's the weather like in Boston, New York, and London today?"
)


@chat.on_user_submit
async def _(message):
    # Unfortunately, Ollama currently doesn't work with tools+streaming
    # https://github.com/ollama/ollama-python/issues/279
    response = llm.response_generator(message, stream=False)
    await chat.append_message_stream(response)
