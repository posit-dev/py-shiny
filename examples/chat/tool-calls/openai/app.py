from typing import Literal

import openai
from pydantic import BaseModel

from shiny.express import ui

llm = openai.AsyncOpenAI()

ui.page_opts(
    title="Hello OpenAI Chat",
    fillable=True,
    fillable_mobile=True,
)

chat = ui.Chat(id="chat")
chat.ui()
chat.update_user_input(
    value="What's the weather like in Boston today? Explain your thought process."
)


def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "celsius"
) -> str:
    return f"The current weather in {location} in {unit} is..."


class Weather(BaseModel):
    location: str
    unit: Literal["celsius", "fahrenheit"] = "celsius"


@chat.on_user_submit
async def _():
    response = await llm.chat.completions.create(
        model="gpt-4o",
        messages=chat.messages(format="openai"),
        stream=True,
        tools=[openai.pydantic_function_tool(Weather)],
        tool_choice="auto",
    )
    await chat.append_message_stream(response, tools=[get_current_weather])


@chat.on_tool_call
async def _():
    response = await llm.chat.completions.create(
        model="gpt-4o",
        messages=chat.messages(format="openai"),  # last message is role:"tool"
        stream=True,
    )
    await chat.append_message_stream(response)
