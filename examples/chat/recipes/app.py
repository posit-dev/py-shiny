# from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI
from utils import recipe_prompt, scrape_page_with_url

from shiny.express import ui

ui.page_opts(
    title="Recipe Extractor Chat",
    fillable=True,
    fillable_mobile=True,
)


# A function to transform user input
# Note that, if an exception occurs, the function will return a message to the user
# "short-circuiting" the conversation and asking the user to try again.
async def transform_user_input(input: str) -> str | dict:
    try:
        return await scrape_page_with_url(input)
    except Exception:
        return {
            "role": "assistant",
            "content": "I'm sorry, I couldn't extract content from that URL. Please try again. ",
        }


# Initialize the chat (with a system prompt and starting message)
chat = ui.Chat(
    id="chat",
    messages=[
        {"role": "system", "content": recipe_prompt},
        {
            "role": "assistant",
            "content": "Hello! I'm a recipe extractor. Please enter a URL to a recipe page. For example, <https://www.thechunkychef.com/epic-dry-rubbed-baked-chicken-wings/>",
        },
    ],
    transform_user_input=transform_user_input,
)

chat.ui(placeholder="Enter a recipe URL...")

llm = AsyncOpenAI()


@chat.on_user_submit
async def _():
    response = await llm.chat.completions.create(
        model="gpt-4o", messages=chat.get_messages(), temperature=0, stream=True
    )
    await chat.append_message_stream(response)
