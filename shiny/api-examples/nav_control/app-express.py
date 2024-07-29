from shiny.express import ui

with ui.navset_card_underline(id="tab"):
    with ui.nav_control():
        ui.a("Shiny", href="https://shiny.posit.co", target="_blank")

    with ui.nav_control():
        ui.a(
            "Learn Shiny",
            href="https://shiny.posit.co/py/docs/overview.html",
            target="_blank",
        )
