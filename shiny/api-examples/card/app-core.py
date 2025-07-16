from shiny import App, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("This is the header"),
        ui.p("This is the body."),
        ui.p("This is still the body."),
        ui.card_footer("This is the footer"),
        full_screen=True,
    ),
)


app = App(app_ui, server=None)
