from openai import AsyncOpenAI

from shiny.express import ui

ui.page_opts(
    title="Hello OpenAI Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create a chat instance
chat = ui.Chat(id="chat")

# Display the chat with an initial message
chat(messages=[{"content": "Hello! How can I help you today?", "role": "assistant"}])

# Create the LLM client (assumes OPENAI_API_KEY is set in the environment)
client = AsyncOpenAI()


# on user submit, generate and append a response
@chat.on_user_submit
async def _():
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=chat.messages(),
        stream=True,
    )
    await chat.append_message_stream(response)
