# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by Google's Gemini model.
# To run it, you'll need a Google API key.
# To get one, follow the instructions at https://ai.google.dev/gemini-api/docs/get-started/tutorial?lang=python
# ------------------------------------------------------------------------------------

from google.generativeai import GenerativeModel

from shiny.express import ui

# You'll need to set the GOOGLE_API_KEY environment variable to your Google API key.
# We recommend putting it in a .env file and loading it with `dotenv`:
# from dotenv import load_dotenv
# _ = load_dotenv()
llm = GenerativeModel()

# Set some Shiny page options
ui.page_opts(
    title="Hello Google Gemini Chat",
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
    messages = chat.messages()

    # Convert messages to the format expected by Google's API
    contents = [
        {
            "role": "model" if x["role"] == "assistant" else x["role"],
            "parts": x["content"],
        }
        for x in messages
    ]

    # Generate a response message stream
    response = llm.generate_content(
        contents=contents,
        stream=True,
    )

    # Append the response stream into the chat
    await chat.append_message_stream(response)
