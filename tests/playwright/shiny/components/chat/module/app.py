from shiny import App, module, ui


@module.ui
def chat_mod_ui():
    return ui.chat_ui(id="chat")


@module.server
def chat_mod_server(input, output, session):
    chat = ui.Chat(id="chat")

    @chat.on_user_submit
    async def _():
        user = chat.user_input()
        await chat.append_message(f"You said: {user}")


app_ui = ui.page_fillable(
    ui.panel_title("Hello Shiny Chat"),
    chat_mod_ui("foo"),
    fillable_mobile=True,
)


def server(input, output, session):
    chat_mod_server("foo")


app = App(app_ui, server)
