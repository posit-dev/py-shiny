# ------------------------------------------------------------------------------------
# A basic Shiny Chat example using Anthropic's Claude model.
# To run it, you'll need an Anthropic API key.
# To get one, follow the instructions at https://docs.anthropic.com/en/api/getting-started
# ------------------------------------------------------------------------------------
import os

from anthropic import AsyncAnthropic

from shiny.express import ui

# Provide your API key here (or set the environment variable)
llm = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Set some Shiny page options
ui.page_opts(
    title="Hello Anthropic Claude Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create and display empty chat
chat = ui.Chat(id="chat")
chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _():
    # Get messages currently in the chat
    messages = chat.get_messages()
    # Create a response message stream
    response = await llm.messages.create(
        model="claude-3-opus-20240229",
        messages=messages,
        stream=True,
        max_tokens=1000,
    )
    # Append the response stream into the chat
    await chat.append_message_stream(response)
