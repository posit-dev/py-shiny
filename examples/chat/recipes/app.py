from langchain_openai import ChatOpenAI
from utils import recipe_prompt, scrape_page_with_url

from shiny.express import ui

ui.page_opts(
    title="Recipe Extractor Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create and display the chat
chat = ui.Chat(
    id="chat",
    messages=[{"role": "system", "content": recipe_prompt}],
    user_input_transformer=scrape_page_with_url,
)
chat.ui(placeholder="Enter a recipe URL...")

llm = ChatOpenAI(temperature=0)


@chat.on_user_submit
async def _():
    response = llm.astream(chat.messages())
    await chat.append_message_stream(response)
