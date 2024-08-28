from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.navset_card_pill(
        ui.nav_menu(
            "Nav Menu items",
            ui.nav_panel("A", "Panel A content"),
            ui.nav_panel("B", "Panel B content"),
            ui.nav_panel("C", "Panel C content"),
        ),
        id="selected_card_pill",
    ),
    ui.h5("Selected:"),
    ui.output_code("selected"),
)


def server(input, output, session):
    @render.code
    def selected():
        return input.selected_card_pill()


app = App(app_ui, server)
