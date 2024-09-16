from shiny.express import ui


def navset_sidebar():
    from shiny import ui as core_ui

    return core_ui.sidebar(core_ui.markdown("Sidebar content"))


ui.page_opts(id="page_navbar_sidebar", sidebar=navset_sidebar())

with ui.nav_panel("Data"):
    "This page could be used to pick a dataset."

with ui.nav_panel("View"):
    "This page could be used to view the dataset."
