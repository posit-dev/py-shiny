from shiny.express import input, render, ui

ui.page_opts(title="Kitchen Sink for input_switch()", fillable=True)

with ui.layout_columns():
    with ui.card():
        ui.h3("Default Switch")
        ui.input_switch("default", "Default switch")

        @render.code
        def default_txt():
            return str(input.default())

    with ui.card():
        ui.h3("With Value")
        ui.input_switch("value", "Preset value", value=True)

        @render.code
        def value_txt():
            return str(input.value())

    with ui.card():
        ui.h3("Custom Width")
        ui.input_switch("width", "Custom width", width="200px")

        @render.code
        def width_txt():
            return str(input.width())
