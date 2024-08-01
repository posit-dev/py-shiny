from shiny import App, ui

app_ui = ui.page_fluid(
    ui.navset_underline(
        ui.nav_panel("A", "Panel A content"),
        ui.nav_panel("B", "Panel B content"),
        ui.nav_panel("C", "Panel C content"),
        ui.nav_menu(
            "Other links",
            ui.nav_panel("D", "Panel D content"),
            "----",
            "Description:",
            ui.nav_control(
                ui.a("Shiny", href="https://shiny.posit.co", target="_blank")
            ),
        ),
        id="tab",
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
