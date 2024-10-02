from chatlas import GoogleChat

from shiny.express import ui

ui.page_opts(
    title="Tool calling with Google",
    fillable=True,
    fillable_mobile=True,
)

# Create and display empty chat
chat = ui.Chat(id="chat")
chat.ui()

# Example from https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb
chat.update_user_input(
    value="I have 57 cats, each owns 44 mittens, how many mittens is that in total?"
)


def add(a: float, b: float):
    """returns a + b."""
    return a + b


def subtract(a: float, b: float):
    """returns a - b."""
    return a - b


def multiply(a: float, b: float):
    """returns a * b."""
    return a * b


def divide(a: float, b: float):
    """returns a / b."""
    return a / b


llm = GoogleChat(
    model="gemini-1.5-flash",
    tools=[add, subtract, multiply, divide],
)


# Generate a response when the user submits a message
@chat.on_user_submit
async def _(message):
    response = llm.response_generator(message)
    await chat.append_message_stream(response)
