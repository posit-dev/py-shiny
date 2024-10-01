from faicons import icon_svg

from shiny.express import input, render, ui

ui.page_opts(title="Kitchen Sink: ui.input_action_link()", fillable=True)

with ui.layout_columns():
    with ui.card():
        ui.input_action_link("default", label="Default action link")

        @render.code
        def default_txt():
            return f"Link clicked {input.default()} times"

    with ui.card():
        ui.input_action_link("icon", "Link with icon", icon=icon_svg("trash-arrow-up"))

        @render.code
        def icon_txt():
            return f"Link clicked {input.icon()} times"
