from shiny.express import input, render, ui

ui.page_opts(title="Checkbox Kitchen Sink", fillable=True)

with ui.layout_columns():
    with ui.card():
        ui.card_header("Default checkbox with label")
        ui.input_checkbox("default", "Basic Checkbox")

        @render.code
        def default_txt():
            return str(input.default())

    with ui.card():
        ui.card_header("Checkbox With Value")
        ui.input_checkbox("value", "Checkbox with Value", value=True)

        @render.code
        def value_txt():
            return str(input.value())

    with ui.card():
        ui.card_header("Checkbox With Width")
        ui.input_checkbox("width", "Checkbox with Width", width="10px")

        @render.code
        def width_txt():
            return str(input.width())
