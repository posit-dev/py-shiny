from shiny.express import input, render, ui

# Set page title
ui.page_opts(full_width=True)

with ui.layout_column_wrap(width=1 / 2):
    with ui.card():
        ui.card_header("Basic Numeric Input")
        ui.input_numeric(id="basic", label="Basic numeric input", value=10)

        @render.text
        def basic_value():
            return f"Current value: {input.basic()}"

    with ui.card():
        ui.card_header("With Min/Max")
        ui.input_numeric(
            id="with_min_max", label="With min and max values", value=5, min=0, max=10
        )

        @render.text
        def minmax_value():
            return f"Current value: {input.with_min_max()}"

    with ui.card():
        ui.card_header("With Step Size")
        ui.input_numeric(
            id="with_step", label="With step size", value=0, min=0, max=100, step=5
        )

        @render.text
        def step_value():
            return f"Current value: {input.with_step()}"

    with ui.card():
        ui.card_header("With Custom Width")
        ui.input_numeric(
            id="with_width", label="With custom width", value=42, width="200px"
        )

        @render.text
        def width_value():
            return f"Current value: {input.with_width()}"
