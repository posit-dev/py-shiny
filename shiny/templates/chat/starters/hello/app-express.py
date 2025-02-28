from shiny.express import expressify, ui


@expressify
def card_suggestion(title: str, suggestion: str, img_src: str, img_alt: str):
    with ui.card(data_suggestion=suggestion):
        ui.card_header(title)
        ui.img(
            src=img_src,
            alt=img_alt,
            style="margin-top:auto; margin-bottom:auto;",
        )


@expressify
def card_suggestions():
    with ui.layout_column_wrap():
        card_suggestion(
            title="Learn Python",
            suggestion="Teach me Python",
            img_src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg",
            img_alt="Python logo",
        )
        card_suggestion(
            title="Learn R",
            suggestion="Teach me R",
            img_src="https://upload.wikimedia.org/wikipedia/commons/1/1b/R_logo.svg",
            img_alt="R logo",
        )


with ui.hold() as suggestions:
    card_suggestions()

welcome = f"""
**Hello!** How can I help you today?

Here are a couple suggestions:

{suggestions[0]}
"""

chat = ui.Chat(
    id="chat",
    messages=[welcome],
)

chat.ui()


@chat.on_user_submit
async def handle_user_input(user_input: str):
    await chat.append_message(f"You said: {user_input}")
