from shiny import reactive
from shiny.express import input, render, ui

ui.input_password("password", "Password:")
ui.input_action_button("go", "Go")


@render.code
@reactive.event(input.go)
def value():
    return input.password()
