from shiny.express import ui

welcome = ui.HTML(
    """
Here is the <span class='suggestion'>1st input suggestion</span>.
And here is a <span data-suggestion='The actual suggestion'>2nd suggestion</span>.
Finally, a <img data-suggestion='A 3rd, image-based, suggestion' src='shiny-hex.svg' height="50px" alt='Shiny logo'> image suggestion.
"""
)

chat = ui.Chat(
    "chat",
    messages=[welcome],
)


chat.ui()


@chat.on_user_submit
async def on_user_submit(message: str):
    await chat.append_message(f"You said: {message}")
