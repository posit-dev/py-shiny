from shiny.express import ui

ui.page_opts(
    id="page_navbar_fillable",
    fillable=True,
    gap="300px",
)

with ui.nav_panel("Data"):
    "This page could be used to pick a dataset."

with ui.nav_panel("View"):
    "This page could be used to view the dataset."
