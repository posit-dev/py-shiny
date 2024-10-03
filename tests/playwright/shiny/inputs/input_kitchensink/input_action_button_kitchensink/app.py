from faicons import icon_svg

from shiny.express import input, render, ui

ui.page_opts(title="Kitchen Sink: ui.input_action_button()", fillable=True)

with ui.layout_columns():
    with ui.card():
        ui.h3("Default Action Button")
        ui.input_action_button("default", label="Default button")

        @render.code
        def default_txt():
            return f"Button clicked {input.default()} times"

    with ui.card():
        ui.h3("With Custom Width")
        ui.input_action_button("width", "Wide button", width="200px")

        @render.code
        def width_txt():
            return f"Button clicked {input.width()} times"

    with ui.card():
        ui.h3("With Icon")
        ui.input_action_button(
            "icon", "Button with icon", icon=icon_svg("trash-arrow-up")
        )

        @render.code
        def icon_txt():
            return f"Button clicked {input.icon()} times"

    with ui.card():
        ui.h3("Disabled Button")
        ui.input_action_button("disabled", "Disabled button", disabled=True)

        @render.code
        def disabled_txt():
            return f"Button clicked {input.disabled()} times"
