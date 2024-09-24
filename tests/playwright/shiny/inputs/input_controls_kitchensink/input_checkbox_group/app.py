from shiny import req
from shiny.express import input, render, ui

ui.page_opts(title="Checkbox Group Kitchen Sink", fillable=True)

choices = ["Option A", "Option B", "Option C", "Option D"]

choices_dict = {
    "value1": "Option A",
    "value2": "Option B",
    "value3": "Option C",
    "value4": "Option D",
}

with ui.layout_columns():
    with ui.card():
        ui.card_header("Default Checkbox Group with label")
        ui.input_checkbox_group("default", "Basic Checkbox Group", choices=choices)

    with ui.card():
        ui.card_header("With Selected Values")
        ui.input_checkbox_group(
            "selected",
            "Selected Values",
            choices=choices,
            selected=["Option B", "Option C"],
        )

    with ui.card():
        ui.card_header("With Width")
        ui.input_checkbox_group("width", "Custom Width", choices=choices, width="30px")

    with ui.card():
        ui.card_header("Inline")
        ui.input_checkbox_group(
            "inline", "Inline Checkbox Group", choices=choices, inline=True
        )

        @render.code
        def inline_val_txt():
            return "You chose " + ", ".join(input.inline())

    with ui.card():
        ui.card_header("With dict of values")
        ui.input_checkbox_group(
            "dict_values",
            "Dict Values",
            choices=choices_dict,
        )

        @render.code
        def dict_value_txt():
            return "You chose " + ", ".join(input.dict_values())
