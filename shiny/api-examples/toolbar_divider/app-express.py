from faicons import icon_svg

from shiny.express import input, render, ui

ui.h2("Toolbar Divider Examples")
ui.p(
    "The toolbar_divider() creates a visual divider line with customizable width and spacing between toolbar elements."
)

with ui.card():
    with ui.card_header():
        "Basic Divider"
        with ui.toolbar(align="right"):
            ui.toolbar_input_button(id="left1", label="Left")
            ui.toolbar_divider()
            ui.toolbar_input_button(id="right1", label="Right")

    with ui.card_body():

        @render.text
        def output_example1():
            left_clicks = input.left1()
            right_clicks = input.right1()
            return f"Left: {left_clicks} clicks | Right: {right_clicks} clicks"


ui.p("Example 2: Custom divider with custom width and gap")

with ui.card():
    with ui.card_header():
        "Custom Divider"
        with ui.toolbar(align="right"):
            ui.toolbar_input_button(id="a", label="A", icon=icon_svg("star"))
            ui.toolbar_divider(width="5px", gap="5rem")
            ui.toolbar_input_button(id="b", label="B", icon=icon_svg("heart"))

    with ui.card_body():

        @render.text
        def output_example2():
            a_clicks = input.a()
            b_clicks = input.b()
            return f"A: {a_clicks} clicks | B: {b_clicks} clicks"
