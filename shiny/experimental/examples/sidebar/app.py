from __future__ import annotations

import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    x.ui.card(
        x.ui.layout_sidebar(
            x.ui.sidebar("Left sidebar content", id="sidebar_left"),
            ui.output_text_verbatim("state_left"),
        )
    ),
    x.ui.card(
        x.ui.layout_sidebar(
            x.ui.sidebar("Right sidebar content", id="sidebar_right", position="right"),
            ui.output_text_verbatim("state_right"),
        ),
    ),
    x.ui.card(
        x.ui.layout_sidebar(
            x.ui.sidebar("Closed sidebar content", id="sidebar_closed", open="closed"),
            ui.output_text_verbatim("state_closed"),
        )
    ),
    x.ui.card(
        x.ui.layout_sidebar(
            x.ui.sidebar("Always sidebar content", id="sidebar_always", open="always"),
            ui.output_text_verbatim("state_always"),
        )
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    def state_left():
        return f"input.sidebar_left(): {input.sidebar_left()}"

    @output
    @render.text
    def state_right():
        return f"input.sidebar_right(): {input.sidebar_right()}"

    @output
    @render.text
    def state_closed():
        return f"input.sidebar_closed(): {input.sidebar_closed()}"

    @output
    @render.text
    def state_always():
        return f"input.sidebar_always(): {input.sidebar_always()}"


app = App(app_ui, server)
