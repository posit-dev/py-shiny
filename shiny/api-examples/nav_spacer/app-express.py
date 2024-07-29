from shiny.express import ui

with ui.navset_underline():
    with ui.nav_panel("Tab 1"):
        "Tab 1 content"
    ui.nav_spacer()
    ui.nav_spacer()
    with ui.nav_panel("Tab 2"):
        "Tab 2 content"
    with ui.nav_panel("Tab 3"):
        "Tab 3 content"
