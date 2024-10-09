from shiny.express import ui

with ui.tooltip(id="default_tooltip_auto"):
    ui.input_action_button("btn", "A button", class_="mt-3")
    "An auto message"

ui.br()
ui.br()

with ui.tooltip(id="default_tooltip_top", placement="top"):
    ui.input_action_button("btn2", "A button", class_="mt-3")
    "A top message"

ui.br()
ui.br()

with ui.tooltip(id="default_tooltip_right", placement="right"):
    ui.input_action_button("btn3", "A button", class_="mt-3")
    "A right message"


ui.br()
ui.br()

with ui.tooltip(id="default_tooltip_left", placement="left"):
    ui.input_action_button("btn4", "A button", class_="mt-3")
    "A left message"
