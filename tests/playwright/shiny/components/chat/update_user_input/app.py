from shiny import reactive
from shiny.express import input, ui

ui.page_opts(fillable=True)

with ui.layout_columns(fill=False, fillable=True):
    ui.input_action_button("set_input", "Just set input")
    ui.input_action_button("set_and_focus", "Set and focus input")
    ui.input_action_button("submit", "Submit to chat")
    ui.input_action_button("submit_and_focus", "Submit and focus chat")

chat = ui.Chat("chat")


chat.ui()


@reactive.effect
@reactive.event(input.set_input)
def do_set_input():
    chat.update_user_input(value="Input was set, but neither focused nor submitted.")


@reactive.effect
@reactive.event(input.set_and_focus)
def do_set_and_focus():
    chat.update_user_input(
        value="Input was set and focused, but not submitted.",
        focus=True,
    )


@reactive.effect
@reactive.event(input.submit)
def do_submit():
    chat.update_user_input(
        value="This chat was sent on behalf of the user.",
        submit=True,
    )


@reactive.effect
@reactive.event(input.submit_and_focus)
def do_submit_and_focus():
    chat.update_user_input(
        value="This chat was sent on behalf of the user. Input will still be focused.",
        submit=True,
        focus=True,
    )


@chat.on_user_submit
async def on_user_submit(message: str):
    await chat.append_message(f"You said: {message}")
