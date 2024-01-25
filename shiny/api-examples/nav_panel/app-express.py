from shiny.express import ui

ui.page_opts(title="Basic Nav Examples")


with ui.navset_tab():
    with ui.nav_panel("One"):
        "First tab content"
    with ui.nav_panel("Two"):
        "Second tab content"
