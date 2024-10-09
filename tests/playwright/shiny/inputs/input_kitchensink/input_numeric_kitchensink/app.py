from shiny.express import input, render, ui

ui.page_opts(title="Kitchen Sink: ui.input_numeric()", fillable=True)

with ui.layout_columns():
    with ui.card():
        ui.h3("Default Numeric Input")
        ui.input_numeric("default", label="Default numeric input", value=10)

        @render.code
        def default_txt():
            return str(input.default())

    with ui.card():
        ui.h3("With Min and Max")
        ui.input_numeric("min_max", "Min and Max", min=0, max=100, value=50)

        @render.code
        def min_max_txt():
            return str(input.min_max())


with ui.layout_columns():
    with ui.card():
        ui.h3("With Step")
        ui.input_numeric("step", "Step of 0.5", step=0.5, value=2.5)

        @render.code
        def step_txt():
            return str(input.step())

    with ui.card():
        ui.h3("Custom Width")
        ui.input_numeric("width", "Custom width", width="200px", value=15)

        @render.code
        def width_txt():
            return str(input.width())
