from shiny import reactive, req
from shiny.express import input, ui

with ui.sidebar():
    ui.input_action_button("update", "Update other buttons and link")

with ui.layout_column_wrap():
    ui.input_action_button("goButton", "Go")
    ui.input_action_button("goButton2", "Go 2", icon="🤩")
    ui.input_action_button("goButton3", "Go 3")
    ui.input_action_link("goLink", "Go Link")


@reactive.effect
def _():
    req(input.update())
    # Updates goButton's label and icon
    ui.update_action_button("goButton", label="New label", icon="📅")
    # Leaves goButton2's label unchanged and removes its icon
    ui.update_action_button("goButton2", icon=[])
    # Leaves goButton3's icon, if it exists, unchanged and changes its label
    ui.update_action_button("goButton3", label="New label 3")
    # Updates goLink's label and icon
    ui.update_action_link("goLink", label="New link label", icon="🔗")
