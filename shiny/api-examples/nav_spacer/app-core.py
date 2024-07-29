from shiny import App, ui

app_ui = ui.page_fluid(
    ui.navset_underline(
        ui.nav_panel("A", "Panel A content"),
        ui.nav_spacer(),
        ui.nav_spacer(),
        ui.nav_panel("B", "Panel B content"),
        ui.nav_panel("C", "Panel C content"),
        id="navset_underline",
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
