from __future__ import annotations

# Import the custom renderer implementations
from renderers import render_capitalize, render_upper

from shiny import App, Inputs, Outputs, Session, ui

app_ui = ui.page_fluid(
    ui.h1("Capitalization renderer"),
    ui.input_text("caption", "Caption:", "Data summary"),
    "@render_upper: ",
    ui.output_text_verbatim("upper", placeholder=True),
    "@render_upper(): ",
    ui.output_text_verbatim("upper_with_paren", placeholder=True),
    "@render_capitalize: ",
    ui.output_text_verbatim("cap_upper", placeholder=True),
    "@render_capitalize(to='lower'): ",
    ui.output_text_verbatim("cap_lower", placeholder=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    # Hovering over `@render_upper` will display the class documentation
    @render_upper
    def upper():
        return input.caption()

    # Hovering over `@render_upper` will display the class documentation as there is no
    # `__init__()` documentation
    @render_upper()
    def upper_with_paren():
        return input.caption()

    # Hovering over `@render_capitalize` will display the class documentation
    @render_capitalize
    def cap_upper():
        return input.caption()

    # Hovering over `@render_capitalize` will display the `__init__()` documentation
    @render_capitalize(to_case="lower")
    def cap_lower():
        return input.caption()


app = App(app_ui, server)
