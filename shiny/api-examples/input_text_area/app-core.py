from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_text_area(
        "caption_regular",
        "Caption:",
        "Data summary\nwith\nmultiple\nlines",
    ),
    ui.output_text_verbatim("value_regular", placeholder=True),
    ui.input_text_area(
        "caption_autoresize",
        ui.markdown("Caption (w/ `autoresize=True`):"),
        "Data summary\nwith\nmultiple\nlines",
        autoresize=True,
    ),
    ui.output_text_verbatim("value_autoresize", placeholder=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def value_regular():
        return input.caption_regular()

    @render.text
    def value_autoresize():
        return input.caption_autoresize()


app = App(app_ui, server)
