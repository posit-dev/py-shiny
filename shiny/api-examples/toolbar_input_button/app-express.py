from faicons import icon_svg

from shiny.express import input, render, ui

ui.h2("Toolbar Input Button Examples")
ui.p(
    "Examples showing different ways to configure toolbar_input_button: label-only, icon-only, and label with icon and custom tooltip."
)

with ui.card():
    with ui.card_header():
        "Label-only Button"
        with ui.toolbar(align="right"):
            ui.toolbar_input_button(id="save", label="Save")

    with ui.card_body():

        @render.text
        def output_example1():
            save_clicks = input.save()
            return f"Save clicks: {save_clicks}"


with ui.card():
    with ui.card_header():
        "Icon-only Button"
        with ui.toolbar(align="right"):
            ui.toolbar_input_button(id="edit", label="Edit", icon=icon_svg("pencil"))

    with ui.card_body():

        @render.text
        def output_example2():
            edit_clicks = input.edit()
            return f"Edit clicks: {edit_clicks}"


with ui.card():
    with ui.card_header():
        "Label and Icon Button"
        with ui.toolbar(align="right"):
            ui.toolbar_input_button(
                id="edit_with_label",
                label="Edit",
                show_label=True,
                icon=icon_svg("pencil"),
                tooltip="Edit Document",
            )

    with ui.card_body():

        @render.text
        def output_example3():
            edit_clicks = input.edit_with_label()
            return f"Edit clicks: {edit_clicks}"
