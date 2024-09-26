from shiny.express import input, render, ui

ui.page_opts(title="Kitchen Sink: ui.input_password()", fillable=True)

with ui.layout_columns():
    with ui.card():
        ui.input_password("default", label="Default password input")

        @render.code
        def default_txt():
            return str(input.default())

    with ui.card():
        ui.input_password(
            "placeholder", "With placeholder", placeholder="Enter password"
        )

        @render.code
        def placeholder_txt():
            return str(input.placeholder())


with ui.layout_columns():
    with ui.card():
        ui.input_password("width", "Custom width", width="200px")

        @render.code
        def width_txt():
            return str(input.width())

    with ui.card():
        ui.input_password("value", "With initial value", value="secret123")

        @render.code
        def value_txt():
            return str(input.value())
