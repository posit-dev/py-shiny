from shiny import reactive
from shiny.express import input, render, ui

ui.input_text("name", "Your Name")
ui.input_action_button("greet", "Say Hello", disabled=True)


@reactive.effect
@reactive.event(input.name)
def set_button_state():
    if input.name():
        ui.update_action_button("greet", disabled=False)
    else:
        ui.update_action_button("greet", disabled=True)


@render.ui
@reactive.event(input.greet)
def hello():
    return ui.p(f"Hello, {input.name()}!", class_="fs-1 text-primary mt-3")
