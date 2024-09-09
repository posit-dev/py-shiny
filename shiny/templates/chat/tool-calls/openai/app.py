from typing import Literal

import openai
from pydantic import BaseModel

from shiny.express import ui

llm = openai.AsyncOpenAI()

ui.page_opts(
    title="Tool calling with OpenAI",
    fillable=True,
    fillable_mobile=True,
)

chat = ui.Chat(
    id="chat",
    messages=["Hello! How can I help you today?"],
)

chat.ui()
chat.update_user_input(
    value="What's the weather like in Boston, New York, and London today?"
)


def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
) -> int:
    if "boston" in location.lower():
        return 12 if unit == "fahrenheit" else -11
    elif "new york" in location.lower():
        return 20 if unit == "fahrenheit" else -6
    else:
        return 72 if unit == "fahrenheit" else 22


class Weather(BaseModel):
    """
    Get the current weather in a given location
    """

    location: str
    unit: Literal["celsius", "fahrenheit"] = "celsius"


_ = Weather.model_rebuild()


@chat.on_user_submit
async def _():
    response = await llm.chat.completions.create(
        model="gpt-4o",
        messages=chat.messages(format="openai"),
        stream=True,
        tools=[openai.pydantic_function_tool(Weather, name="get_current_weather")],
        tool_choice="auto",
    )
    await chat.append_message_stream(response)


chat.bind_tools(get_current_weather)


# TODO: allow this decorator to be stacked
@chat.on_tool_result
async def _():
    response = await llm.chat.completions.create(
        model="gpt-4o",
        messages=chat.messages(format="openai"),  # last message is role:"tool"
        stream=True,
        tools=[openai.pydantic_function_tool(Weather, name="get_current_weather")],
        tool_choice="auto",
    )
    await chat.append_message_stream(response)
