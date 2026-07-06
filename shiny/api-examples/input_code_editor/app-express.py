from shiny.express import input, render, ui

ui.page_opts(fillable=True)

with ui.layout_columns(col_widths=[6, 6]):
    with ui.card():
        ui.card_header("Python Code Editor")
        ui.input_code_editor(
            "code",
            label="Enter Python code:",
            value="def greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('World'))",
            language="python",
            height="200px",
        )

    with ui.card():
        ui.card_header("Editor Value")

        @render.text
        def value():
            return input.code()
