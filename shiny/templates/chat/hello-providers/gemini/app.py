# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by Google's Gemini model.
# To run it, you'll need a Google API key.
# To get one, follow the instructions at https://ai.google.dev/gemini-api/docs/get-started/tutorial?lang=python
# ------------------------------------------------------------------------------------
from app_utils import load_dotenv
from google.generativeai import GenerativeModel

from shiny.express import ui

# Either explicitly set the GOOGLE_API_KEY environment variable before launching the
# app, or set them in a file named `.env`. The `python-dotenv` package will load `.env`
# as environment variables which can later be read by `os.getenv()`.
load_dotenv()
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
    contents = chat.messages(format="google")

    # Generate a response message stream
    response = llm.generate_content(
        contents=contents,
        stream=True,
    )

    # Append the response stream into the chat
    await chat.append_message_stream(response)
