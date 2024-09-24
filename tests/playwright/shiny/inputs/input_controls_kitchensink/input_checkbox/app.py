from shiny.express import ui

ui.page_opts(title="Checkbox Kitchen Sink", fillable=True)

with ui.layout_columns():
    with ui.card():
        ui.card_header("Default checkbox with label")
        ui.input_checkbox("default", "Basic Checkbox")

    with ui.card():
        ui.card_header("Checkbox With Value")
        ui.input_checkbox("value", "Checkbox with Value", value=True)

    with ui.card():
        ui.card_header("Checkbox With Width")
        ui.input_checkbox("width", "Checkbox with Width", width="10px")
