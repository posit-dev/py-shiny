from shiny import App, ui

app_ui = ui.page_sidebar(
    ui.sidebar("Sidebar content"),
    "Main content",
)

app = App(app_ui, server=None)
