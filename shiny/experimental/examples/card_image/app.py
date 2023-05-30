from __future__ import annotations

import shiny.experimental as x
from shiny import App, ui

app_ui = ui.page_fluid(
    ui.tags.style(
        """
        .card-body {
            border: 1px dashed red;
        }
        """
    ),
    x.ui.card(
        x.ui.card_header(
            "These two images are in their own individual card_body() container"
        ),
        x.ui.card_image(
            file=None,
            src="https://posit.co/wp-content/uploads/2022/10/Posit-logo-h-full-color-RGB-TM.svg",
        ),
        x.ui.card_image(
            file=None,
            src="https://posit.co/wp-content/uploads/2022/10/Posit-logo-h-full-color-RGB-TM.svg",
        ),
        x.ui.card_header("These two images are in the same card_body() container"),
        x.ui.card_image(
            file=None,
            src="https://posit.co/wp-content/uploads/2022/10/Posit-logo-h-full-color-RGB-TM.svg",
            container=ui.tags.span,
        ),
        x.ui.card_image(
            file=None,
            src="https://posit.co/wp-content/uploads/2022/10/Posit-logo-h-full-color-RGB-TM.svg",
            container=ui.tags.span,
        ),
    ),
)


app = App(app_ui, server=None)
