from shiny.express import render, ui

chat = ui.Chat(id="chat")


@render.ui
def chat_output():
    return chat.ui(messages=["A starting message"])
