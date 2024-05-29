from google.generativeai import GenerativeModel

from shiny.express import ui

ui.page_opts(
    title="Hello Google Gemini Chat",
    fillable=True,
    fillable_mobile=True,
)

# create a chat instance
chat = ui.Chat(id="chat")

# display the chat
chat

# create an LLM client
client = GenerativeModel()


# on user submit, generate and append a response
@chat.on_user_submit
async def _():
    messages = chat.messages()

    # Convert messages to the format expected by Google's API
    # TODO: we could automatically do this if client is provided?
    contents = [
        {
            "role": "model" if x["role"] == "assistant" else x["role"],
            "parts": x["content"],
        }
        for x in messages
    ]

    response = client.generate_content(
        contents=contents,
        stream=True,
    )
    await chat.append_message_stream(response)