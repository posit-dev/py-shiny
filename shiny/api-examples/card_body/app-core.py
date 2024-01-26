import shiny.experimental as x
from shiny import App, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("This is the header"),
        x.ui.card_body(
            x.ui.card_title("This is the title"),
            ui.p("This is the body."),
            ui.p("This is still the body."),
        ),
        ui.card_footer("This is the footer"),
        full_screen=True,
    ),
    ui.card(
        ui.p("These first two elements will be wrapped in `card_body()` together."),
        ui.p("These first two elements will be wrapped in `card_body()` together."),
        x.ui.card_body(ui.p("A card body.")),
        ui.p("These last two elements will be wrapped in `card_body()` together."),
        ui.p("These last two elements will be wrapped in `card_body()` together."),
    ),
)


app = App(app_ui, server=None)
