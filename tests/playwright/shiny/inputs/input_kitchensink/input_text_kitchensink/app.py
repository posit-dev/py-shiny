from shiny.express import input, render, ui

ui.page_opts(title="Kitchen Sink: ui.input_text()", fillable=True)

with ui.layout_columns():
    with ui.card():
        ui.input_text("default", label="Default text input")

        @render.code
        def default_txt():
            return str(input.default())

    with ui.card():
        ui.input_text("placeholder", "With placeholder", placeholder="Enter text here")

        @render.code
        def placeholder_txt():
            return str(input.placeholder())


with ui.layout_columns():
    with ui.card():
        ui.input_text(
            "width", "Custom width", width="200px", value="Custom width input"
        )

        @render.code
        def width_txt():
            return str(input.width())

    with ui.card():
        ui.input_text("autocomplete", "autocomplete input", autocomplete="on")

        @render.code
        def autocomplete_txt():
            return str(input.autocomplete())


with ui.layout_columns():
    with ui.card():
        ui.input_text(
            "spellcheck", "spellcheck input", value="paticular", spellcheck="true"
        )

        @render.code
        def spellcheck_txt():
            return str(input.spellcheck())
