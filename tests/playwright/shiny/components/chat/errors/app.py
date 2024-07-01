from shiny.express import ui

# Set some Shiny page options
ui.page_opts(title="Hello Chat")


chat = ui.Chat(id="chat")
chat.ui()


@chat.on_user_submit
async def _():
    raise Exception("boom!")
