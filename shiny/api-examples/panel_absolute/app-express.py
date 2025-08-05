from shiny.express import ui

ui.h2("A basic absolute panel example")

with ui.panel_absolute(draggable=True, width="300px", right="50px", top="25%"):
    with ui.card():
        ui.card_header("Drag me around!")
        ui.input_slider("n", "N", min=0, max=100, value=20)
