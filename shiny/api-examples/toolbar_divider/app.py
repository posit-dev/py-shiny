from faicons import icon_svg

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar Divider Examples"),
    ui.p(
        "The toolbar_divider() creates a visual divider line with customizable width and spacing between toolbar elements."
    ),
    ui.card(
        ui.card_header(
            "Basic Divider",
            ui.toolbar(
                ui.toolbar_input_button(id="left1", label="Left"),
                ui.toolbar_divider(),
                ui.toolbar_input_button(id="right1", label="Right"),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_example1"),
        ),
    ),
    ui.p("Example 2: Custom divider with custom width and gap"),
    ui.card(
        ui.card_header(
            "Custom Divider",
            ui.toolbar(
                ui.toolbar_input_button(id="a", label="A", icon=icon_svg("star")),
                ui.toolbar_divider(width="5px", gap="5rem"),
                ui.toolbar_input_button(id="b", label="B", icon=icon_svg("heart")),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_example2"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @output
    @render.text
    def output_example1():
        left_clicks = input.left1()
        right_clicks = input.right1()
        return f"Left: {left_clicks} clicks | Right: {right_clicks} clicks"

    @output
    @render.text
    def output_example2():
        a_clicks = input.a()
        b_clicks = input.b()
        return f"A: {a_clicks} clicks | B: {b_clicks} clicks"


app = App(app_ui, server)
