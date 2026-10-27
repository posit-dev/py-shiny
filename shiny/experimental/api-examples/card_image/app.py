from pathlib import Path

import shiny.experimental as x
from shiny import App, ui

logo = Path(__file__).parent / "posit-logo.png"

app_ui = ui.page_fluid(
    ui.tags.style("""
        .card-body {
            border: 1px dashed red;
        }
        """),
    x.ui.card(
        ui.card_header(
            "These two images are in their own individual card_body() container"
        ),
        x.ui.card_image(file=logo),
        x.ui.card_image(file=logo),
        ui.card_header("These two images are in the same card_body() container"),
        x.ui.card_image(file=logo, container=ui.tags.span),
        x.ui.card_image(file=logo, container=ui.tags.span),
    ),
)


app = App(app_ui, server=None)
