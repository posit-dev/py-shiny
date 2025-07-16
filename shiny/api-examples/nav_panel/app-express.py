from shiny.express import ui

ui.page_opts(title="Nav Panel Example")

with ui.nav_panel("Page 1"):
    "Page 1 content"

with ui.nav_panel("Page 2"):
    with ui.navset_card_underline():
        with ui.nav_panel("Tab 1"):
            "Tab 1 content"
        with ui.nav_panel("Tab 2"):
            "Tab 2 content"
        with ui.nav_panel("Tab 3"):
            "Tab 3 content"
