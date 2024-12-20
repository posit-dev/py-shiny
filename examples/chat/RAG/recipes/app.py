# ------------------------------------------------------------------------------------
# A simple recipe extractor chatbot that extracts recipes from URLs using the OpenAI API.
# To run it, you'll need an OpenAI API key.
# To get one, follow the instructions at https://platform.openai.com/docs/quickstart
# ------------------------------------------------------------------------------------
import os

from chatlas import ChatOpenAI
from utils import recipe_prompt, scrape_page_with_url

from shiny.express import ui

# Provide your API key here (or set the environment variable)
chat_model = ChatOpenAI(
    system_prompt=recipe_prompt,
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Set some Shiny page options
ui.page_opts(
    title="Recipe Extractor Chat",
    fillable=True,
    fillable_mobile=True,
)

# Initialize the chat (with a system prompt and starting message)
chat = ui.Chat(
    id="chat",
    messages=[
        "Hello! I'm a recipe extractor. Please enter a URL to a recipe page. For example, <https://www.thechunkychef.com/epic-dry-rubbed-baked-chicken-wings/>"
    ],
)

chat.ui(placeholder="Enter a recipe URL...")


# A function to transform user input
# Note that, if an exception occurs, the function will return a message to the user
# "short-circuiting" the conversation and asking the user to try again.
@chat.transform_user_input
async def try_scrape_page(input: str) -> str | None:
    try:
        return await scrape_page_with_url(input)
    except Exception:
        await chat.append_message(
            "I'm sorry, I couldn't extract content from that URL. Please try again. "
        )
        return None


@chat.on_user_submit
async def handle_user_input(user_input: str):
    response = chat_model.stream(
        user_input,
        kwargs={"temperature": 0},
    )
    await chat.append_message_stream(response)
