from shiny.express import input, render, ui

with ui.navset_card_pill(id="selected_card_pill"):
    with ui.nav_menu("Nav Menu items"):
        with ui.nav_panel("A"):
            "Page A content"
        with ui.nav_panel("B"):
            "Page B content"
        with ui.nav_panel("C"):
            "Page C content"
ui.h5("Selected:")


@render.code
def _():
    return input.selected_card_pill()
