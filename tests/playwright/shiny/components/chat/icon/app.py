import asyncio

import faicons

from shiny.express import input, ui

ui.page_opts(title="Chat Icons")

with ui.layout_columns():
    # Default Bot ---------------------------------------------------------------------
    chat_default = ui.Chat(
        id="chat_default",
        messages=[
            {
                "content": "Hello! I'm Default Bot. How can I help you today?",
                "role": "assistant",
            },
        ],
    )

    with ui.div():
        ui.h2("Default Bot")
        chat_default.ui(icon_assistant=None)

    @chat_default.on_user_submit
    async def handle_user_input_default(user_input: str):
        await asyncio.sleep(1)
        await chat_default.append_message(f"You said: {user_input}")

    # Animal Bot ----------------------------------------------------------------------
    chat_animal = ui.Chat(
        id="chat_animal",
        messages=[
            {
                "content": "Hello! I'm Animal Bot. How can I help you today?",
                "role": "assistant",
            },
        ],
    )

    with ui.div():
        ui.h2("Animal Bot")
        chat_animal.ui(icon_assistant=faicons.icon_svg("otter").add_class("icon-otter"))
        ui.input_select("animal", "Animal", choices=["Otter", "Hippo", "Frog", "Dove"])

    @chat_animal.on_user_submit
    async def handle_user_input_otter(user_input: str):
        await asyncio.sleep(1)
        icon_name = input.animal().lower()
        if icon_name == "Otter":
            # Don't include the icon in the custom message, i.e. use default icon
            icon = None
        else:
            icon = faicons.icon_svg(icon_name).add_class(f"icon-{icon_name}")

        await chat_animal.append_message(
            f"{input.animal()} said: {user_input}",
            icon=icon,
        )

    # SVG Bot -------------------------------------------------------------------------
    bs_icon_info_circle_fill = """
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-info-circle-fill icon-svg" viewBox="0 0 16 16">
    <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16m.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2"/>
    </svg>
    """

    chat_svg = ui.Chat(
        id="chat_svg",
        messages=[
            {
                "content": "Hello! I'm SVG Bot. How can I help you today?",
                "role": "assistant",
            },
        ],
    )

    with ui.div():
        ui.h2("SVG Bot")
        chat_svg.ui(icon_assistant=ui.HTML(bs_icon_info_circle_fill))

    @chat_svg.on_user_submit
    async def handle_user_input_svg(user_input: str):
        await chat_svg.append_message(f"You said: {user_input}")

    # Shiny Bot -----------------------------------------------------------------------
    chat_shiny = ui.Chat(
        id="chat_shiny",
        messages=[
            {
                "content": "Hello! I'm Shiny Bot. How can I help you today?",
                "role": "assistant",
            },
        ],
    )

    with ui.div():
        ui.h2("Shiny Bot")
        chat_shiny.ui(
            icon_assistant=ui.img(
                src="https://github.com/rstudio/hex-stickers/raw/refs/heads/main/PNG/shiny.png",
                class_="icon-shiny",
            )
        )

    @chat_shiny.on_user_submit
    async def handle_user_input_shiny(user_input: str):
        await chat_shiny.append_message(f"You said: {user_input}")
