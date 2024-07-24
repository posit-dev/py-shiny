from shiny.express import render, ui

# Set some Shiny page options
ui.page_opts(title="Hello Chat")


chat = ui.Chat(id="chat")
chat.ui()


@chat.on_user_submit
async def _():
    raise Exception("boom!")


# Placeholder to help determine when shiny has loaded via `.shiny-bound-output` being present
@render.ui
def _():
    return ""
