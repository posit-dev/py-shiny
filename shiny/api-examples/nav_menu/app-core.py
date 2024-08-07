from shiny import App, ui

app_ui = ui.page_fluid(
    ui.navset_card_pill(
        ui.nav_menu(
            "Nav Menu items",
            ui.nav_panel("A", "Panel A content"),
            ui.nav_panel("B", "Panel B content"),
            ui.nav_panel("C", "Panel C content"),
        ),
        id="card_pill",
    ),
)


def server(input, output, session):
    pass


app = App(app_ui, server)
