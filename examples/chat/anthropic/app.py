from anthropic import AsyncAnthropic

from shiny.express import ui

ui.page_opts(
    title="Hello Anthropic Claude Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create a chat instance
chat = ui.Chat(id="chat")

# Display the chat
chat()

# Create the LLM client (assumes ANTHROPIC_API_KEY is set in the environment)
client = AsyncAnthropic()


# on user submit, generate and append a response
@chat.on_user_submit
async def _():
    response = await client.messages.create(
        model="claude-3-opus-20240229",
        messages=chat.messages(),
        stream=True,
        max_tokens=1000,
    )
    await chat.append_message_stream(response)
