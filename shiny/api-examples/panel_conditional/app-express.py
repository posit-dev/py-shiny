from shiny.express import ui

ui.input_checkbox("show", "Show radio buttons", False)

with ui.panel_conditional("input.show"):
    ui.input_radio_buttons("radio", "Choose ", ["slider", "select"])

with ui.panel_conditional("input.show && input.radio === 'slider'"):
    ui.input_slider("slider", None, min=0, max=100, value=50)

with ui.panel_conditional("input.show && input.radio === 'select'"):
    ui.input_select("select", None, ["A", "B", "C"])
