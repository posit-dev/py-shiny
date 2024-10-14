from shiny.express import input, render, ui

ui.page_opts(title="Kitchen Sink: ui.input_radio_buttons()", fillable=True)

options = ["Option A", "Option B", "Option C"]
options_dict = {"a": "Option A", "b": "Option B", "c": "Option C"}

with ui.layout_columns():
    with ui.card():
        ui.h3("Default Radio Buttons")
        ui.input_radio_buttons("default", "Default radio buttons", options)

        @render.code
        def default_txt():
            return str(input.default())

    with ui.card():
        ui.h3("With Selected Value")
        ui.input_radio_buttons("selected", "Preset value", options, selected="Option B")

        @render.code
        def selected_txt():
            return str(input.selected())

    with ui.card():
        ui.h3("Inline Layout")
        ui.input_radio_buttons("inline", "Inline layout", options, inline=True)

        @render.code
        def inline_txt():
            return str(input.inline())


with ui.layout_columns():
    with ui.card():
        ui.h3("Custom Width")
        ui.input_radio_buttons("width", "Custom width", options, width="30px")

        @render.code
        def width_txt():
            return str(input.width())

    with ui.card():
        ui.h3("With Named List")
        ui.input_radio_buttons("choices_dict", "Named list options", options_dict)

        @render.code
        def choices_dict_txt():
            return str(input.choices_dict())
