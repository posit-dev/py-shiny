from shiny import App, ui

app_ui = ui.page_fluid(
    ui.navset_card_underline(
        ui.nav_control(ui.a("Shiny", href="https://shiny.posit.co", target="_blank")),
        ui.nav_control(
            ui.a(
                "Learn Shiny",
                href="https://shiny.posit.co/py/docs/overview.html",
                target="_blank",
            )
        ),
    ),
    id="tab",
)


def server(input, output, session):
    pass


app = App(app_ui, server)
