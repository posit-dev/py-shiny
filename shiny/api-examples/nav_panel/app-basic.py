from shiny import App, Inputs, ui

app_ui = ui.page_fixed(
    ui.panel_title("Basic Nav Example"),
    ui.navset_tab(
        ui.nav_panel("One", "First tab content."),
        ui.nav_panel("Two", "Second tab content."),
    ),
)


def server(input: Inputs):
    pass


app = App(app_ui, server)
