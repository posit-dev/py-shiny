# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by OpenAI's GPT-4o model using the `litellm` library.
# To run it, you'll need OpenAI API key.
# To get setup, follow the instructions at https://platform.openai.com/docs/quickstart
# ------------------------------------------------------------------------------------
import litellm

from shiny.express import ui
from shiny.ui._chat_tools import func_to_schema

chat = ui.Chat(id="chat")
# chat = ui.Chat(id="chat", strategy=LangChain(base_url="https://api.openai.com"))
chat.ui()
chat.update_user_input(
    value="What's the weather like in Boston today? Explain your thought process."
)


def get_current_weather(location: str, unit: str):
    """Get the current weather in a given location

    Parameters
    ----------
    location : str
        The city and state, e.g. San Francisco, CA
    unit : {'celsius', 'fahrenheit'}
        Temperature unit

    Returns
    -------
    str
        a sentence indicating the weather
    """
    if location == "Boston, MA":
        return "The weather is 12F"


@chat.on_user_submit
async def _():
    messages = chat.messages()
    response = await litellm.acompletion(
        model="gpt-4o",
        messages=messages,
        # TODO: fix this issue so folks can use litellm
        # https://github.com/posit-dev/py-shiny/issues/1675
        tools=[func_to_schema(get_current_weather)],
        stream=True,
    )
    await chat.append_message_stream(response)


chat.bind_tools(get_current_weather)


@chat.on_tool_result
async def _():
    print("On tool result")
    print(chat.messages())
    response = await litellm.acompletion(
        model="gpt-4o",
        messages=chat.messages(),  # Last message contains the tool result
        stream=True,
    )
    await chat.append_message_stream(response)


# chat.register_tool(get_current_weather, model="gpt-4o")
