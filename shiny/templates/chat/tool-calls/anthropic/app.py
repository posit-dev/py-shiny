from typing import Literal

from anthropic import AsyncAnthropic

from shiny.express import ui

ui.page_opts(
    title="Tool calling with Anthropic",
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


# Define a (function) tool
def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
) -> int:
    if "boston" in location.lower():
        return 12 if unit == "fahrenheit" else -11
    elif "new york" in location.lower():
        return 20 if unit == "fahrenheit" else -6
    else:
        return 72 if unit == "fahrenheit" else 22


llm = AsyncAnthropic()
MODEL = "claude-3-5-sonnet-20240620"
TOOLS = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The unit of temperature, either 'celsius' or 'fahrenheit'",
                },
            },
            "required": ["location"],
        },
    }
]


@chat.on_user_submit
async def _():
    response = await llm.messages.create(
        model=MODEL,
        messages=chat.messages(format="anthropic"),
        stream=True,
        tools=TOOLS,
        max_tokens=1000,
    )
    await chat.append_message_stream(response)


chat.bind_tools(get_current_weather)


@chat.on_tool_result
async def _():
    messages = chat.messages(format="anthropic")

    # If we see consecutive user messages, combine their conten into a single message
    # This is needed since we currently create one tool message per tool call, but
    # anthropic requires them to be combined into a single user message
    # TODO: This should be handled somewhere else
    from itertools import groupby

    final_messages = []
    for role, group in groupby(messages, key=lambda x: x["role"]):
        group_list = list(group)
        if role != "user":
            final_messages.extend(group_list)
            continue
        content = []
        for g in group_list:
            content.append(g["content"][0])
        final_messages.append({"content": content, "role": "user"})

    response = await llm.messages.create(
        model=MODEL,
        messages=final_messages,
        stream=True,
        tools=TOOLS,
        max_tokens=1000,
    )
    await chat.append_message_stream(response)
