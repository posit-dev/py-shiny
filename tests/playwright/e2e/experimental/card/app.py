import shiny.experimental as x
from shiny import App, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("This is the header"),
        x.ui.card_title("This is the title"),
        ui.p("This is the body."),
        x.ui.card_image(
            file=None,
            src="https://posit.co/wp-content/uploads/2022/10/Posit-logo-h-full-color-RGB-TM.svg",
        ),
        ui.p("This is still the body."),
        ui.card_footer("This is the footer"),
        full_screen=True,
        id="card1",
    ),
)


app = App(app_ui, server=None)
