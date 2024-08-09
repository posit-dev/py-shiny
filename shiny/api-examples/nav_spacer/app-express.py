from shiny.express import input, render, ui

with ui.navset_underline(id="selected_navset_underline"):
    with ui.nav_panel("Tab 1"):
        "Tab 1 content"
    ui.nav_spacer()
    with ui.nav_panel("Tab 2"):
        "Tab 2 content"
    with ui.nav_panel("Tab 3"):
        "Tab 3 content"
ui.h5("Selected:")


@render.code
def _():
    return input.selected_navset_underline()
