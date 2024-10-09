from shiny.express import ui

ui.page_opts(
    id="default_page_navbar",
    title="Default Page Navbar",
    window_title="Page NavBar title",
    lang="en",
    fillable_mobile=True,
    fillable=True,
)

with ui.nav_panel("Data"):
    "This page could be used to pick a dataset."

with ui.nav_panel("View"):
    "This page could be used to view the dataset."
