from shiny.express import ui

ui.page_opts(
    id="page_navbar_header_footer_fixed_top",
    header=ui.tags.div("Header", id="page_navbar_header"),
    footer=ui.tags.div("Footer", id="page_navbar_footer"),
    position="fixed-top",
    fluid=False,
)

with ui.nav_panel("Data"):
    "This page could be used to pick a dataset."

with ui.nav_panel("View"):
    "This page could be used to view the dataset."
