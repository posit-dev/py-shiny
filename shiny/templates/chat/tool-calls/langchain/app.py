from typing import Literal

from langchain_core.tools import tool
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


llm = ChatOpenAI()


def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
) -> int:
    """
    Get the current weather in a given location
    """
    if "boston" in location.lower():
        return 12 if unit == "fahrenheit" else -11
    elif "new york" in location.lower():
        return 20 if unit == "fahrenheit" else -6
    else:
        return 72 if unit == "fahrenheit" else 22


llm_with_tools = llm.bind_tools(
    [
        tool(get_current_weather),
    ]
)


@chat.on_user_submit
async def _():
    messages = chat.messages(format="langchain")
    response = llm_with_tools.astream(messages)
    await chat.append_message_stream(response)


# TODO: support the tool() result type from langchain?
chat.bind_tools(get_current_weather)


@chat.on_tool_result
async def _():
    messages = chat.messages(format="langchain")  # last message is role:"tool"
    response = llm_with_tools.astream(messages)
    await chat.append_message_stream(response)
