from chatlas import LangChainChat
from langchain_openai import ChatOpenAI

from shiny.express import ui

ui.page_opts(
    title="Tool calling with LangChain",
    fillable=True,
    fillable_mobile=True,
)


chat = ui.Chat(id="chat")
chat.ui()
chat.update_user_input(
    value="What's the weather like in Boston, New York, and London today?"
)


@chat.on_user_submit
async def _(message):
    response = llm.response_generator(message)
    await chat.append_message_stream(response)


def get_current_weather(location: str, unit: str = "fahrenheit") -> int:
    """
    Get the current weather in a given location
    """
    if "boston" in location.lower():
        return 12 if unit == "fahrenheit" else -11
    elif "new york" in location.lower():
        return 20 if unit == "fahrenheit" else -6
    else:
        return 72 if unit == "fahrenheit" else 22


llm = LangChainChat(
    ChatOpenAI(model="gpt-4o"),
    system_prompt="You are a helpful assistant.",
    tools=[get_current_weather],
)
