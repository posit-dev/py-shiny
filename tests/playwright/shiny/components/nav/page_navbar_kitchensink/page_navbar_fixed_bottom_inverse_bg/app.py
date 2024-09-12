from shiny.express import ui

ui.page_opts(
    id="page_fixed_bottom_inverse_bg",
    position="fixed-bottom",
    bg="dodgerBlue",
    inverse=True,
)

with ui.nav_panel("Data"):
    "This page could be used to pick a dataset."

with ui.nav_panel("View"):
    "This page could be used to view the dataset."
