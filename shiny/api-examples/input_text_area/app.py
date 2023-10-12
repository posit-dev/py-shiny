import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    x.ui.input_text_area(
        "caption_regular",
        "Caption:",
        "Data summary\nwith\nmultiple\nlines",
    ),
    ui.output_text_verbatim("value_regular", placeholder=True),
    x.ui.input_text_area(
        "caption_resize",
        ui.markdown("Caption (w/ `autoresize=True`):"),
        "Data summary\nwith\nmultiple\nlines",
        autoresize=True,
    ),
    ui.output_text_verbatim("value_resize", placeholder=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    def value_regular():
        return input.caption_regular()

    @output
    @render.text
    def value_resize():
        return input.caption_resize()


app = App(app_ui, server)
