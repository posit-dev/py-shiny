from shiny.express import ui
from shiny.ui._chat_client_openai import OpenAIClient

ui.page_opts(
    title="Tool calling with OpenAI",
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


llm = OpenAIClient(
    model="gpt-4o",
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
async def _(input):
    response = llm.generate_response(input)
    await chat.append_message_stream(response)
