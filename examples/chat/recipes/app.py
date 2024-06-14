# import shiny_validate as sv
from langchain_openai import ChatOpenAI
from utils import recipe_prompt, scrape_page_with_url

from shiny.express import ui

ui.page_opts(
    title="Recipe Extractor Chat",
    fillable=True,
    fillable_mobile=True,
)


# Create a subclass of ui.Chat to handle the recipe extraction
class RecipeChat(ui.Chat):
    async def transform_user_input(self, input: str) -> str:
        return await scrape_page_with_url(input)


# Initialize the chat (with a system prompt and starting message)
chat = RecipeChat(
    id="chat",
    messages=[
        {"role": "system", "content": recipe_prompt},
        {
            "role": "assistant",
            "content": "Hello! I'm a recipe extractor. Please enter a URL to a recipe page. For example, <https://www.thechunkychef.com/epic-dry-rubbed-baked-chicken-wings/>",
        },
    ],
)

chat.ui(placeholder="Enter a recipe URL...")

llm = ChatOpenAI(temperature=0)

# TODO: get input validation working
# iv = sv.InputValidator()
# iv.add_rule(chat.user_input_id, sv.check.url())


@chat.on_user_submit
async def _():
    # iv.enable()
    response = await llm.ainvoke(chat.get_messages())
    await chat.append_message(response)
