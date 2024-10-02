from shiny.express import input, render, ui

ui.page_opts(title="Kitchen Sink: ui.input_text_area()", fillable=True)

with ui.layout_columns():
    with ui.card():
        ui.input_text_area("default", label="Default text area")

        @render.code
        def default_txt():
            return str(input.default())

    with ui.card():
        ui.input_text_area(
            "placeholder", "With placeholder", placeholder="Enter text here"
        )

        @render.code
        def placeholder_txt():
            return str(input.placeholder())


with ui.layout_columns():
    with ui.card():
        ui.input_text_area(
            "custom_size",
            "Custom size",
            width="300px",
            height="150px",
            value="Resized text area",
        )

        @render.code
        def custom_size_txt():
            return str(input.custom_size())

    with ui.card():
        ui.input_text_area(
            "rows",
            "Custom rows",
            rows=5,
            value="This text area has 5 rows",
            resize="none",
        )

        @render.code
        def rows_txt():
            return str(input.rows())

    with ui.card():
        ui.input_text_area(
            "cols", "Custom cols", cols=30, value="This text area has 30 cols"
        )

        @render.code
        def cols_txt():
            return str(input.cols())


with ui.layout_columns():
    with ui.card():
        ui.input_text_area(
            "autocomplete", "Autocomplete", autocomplete="name", resize="horizontal"
        )

        @render.code
        def autocomplete_txt():
            return str(input.autocomplete())

    with ui.card():
        ui.input_text_area(
            "resize", "Resizable", value="You can resize this text area", resize="both"
        )

        @render.code
        def resize_txt():
            return str(input.resize())

    with ui.card():
        ui.input_text_area(
            "spellcheck",
            "Spellcheck",
            value="paticular",
            spellcheck="true",
            resize="vertical",
        )

        @render.code
        def spellcheck_txt():
            return str(input.spellcheck())
