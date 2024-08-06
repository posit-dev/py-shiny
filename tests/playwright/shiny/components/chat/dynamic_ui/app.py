from shiny.express import render, ui

chat = ui.Chat(id="chat", messages=["A starting message"])


@render.ui
def chat_output():
    return chat.ui()
