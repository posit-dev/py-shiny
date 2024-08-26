from shiny import App, Inputs, ui

app_ui = ui.page_fluid(
    ui.navset_bar(
        ui.nav_panel("Page 1", "Page 1 content"),
        ui.nav_panel(
            "Page 2",
            ui.navset_card_underline(
                ui.nav_panel("Tab 1", "Tab 1 content"),
                ui.nav_panel("Tab 2", "Tab 2 content"),
                ui.nav_panel("Tab 3", "Tab 3 content"),
            ),
        ),
        title="Nav Panel Example",
    ),
)


def server(input: Inputs):
    pass


app = App(app_ui, server)
