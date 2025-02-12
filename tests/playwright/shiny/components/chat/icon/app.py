import faicons

from shiny import Inputs, Outputs, Session
from shiny.express import module, ui

ui.page_opts(title="Chat Icons")

# Icons ----
bs_icon_info_circle_fill = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-info-circle-fill icon-svg" viewBox="0 0 16 16">
  <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16m.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2"/>
</svg>
"""

otter = faicons.icon_svg("otter").add_class("icon-otter")

shiny = ui.img(
    src="https://github.com/rstudio/hex-stickers/raw/refs/heads/main/SVG/shiny.svg",
    class_="icon-shiny",
)


@module
def chat_component(
    input: Inputs,
    output: Outputs,
    session: Session,
    icon: ui.HTML | ui.Tag | None,
    title: str,
):
    chat = ui.Chat(
        id="chat",
        messages=[
            {
                "content": f"Hello! I'm {title}. How can I help you today?",
                "role": "assistant",
            },
        ],
    )

    with ui.div():
        ui.h2(title)
        chat.ui(icon_assistant=icon)

    # Define a callback to run when the user submits a message
    @chat.on_user_submit
    async def handle_user_input(user_input: str):
        await chat.append_message(f"You said: {user_input}")


with ui.layout_columns():
    chat_component("default", None, "Default Bot")

    chat_component("otter", otter, "Otter Bot")

    chat_component("svg", ui.HTML(bs_icon_info_circle_fill), "SVG Bot")

    chat_component("shiny", shiny, "Shiny Bot")
