from shiny.express import ui

ui.page_opts(title="App with Navbar", fillable=True, id="page")

with ui.sidebar():
    ui.input_select("data", "Dataset", ("tips", "flights", "exercise"))

    with ui.panel_conditional("input.page === 'View'"):
        ui.input_select("view", "View", ("plot", "table"))

ui.nav_spacer()

with ui.nav_panel("Data"):
    "This page could be used to pick a dataset."

with ui.nav_panel("View"):
    "This page could be used to view the dataset."
    "Notice the additional controls that appear when 'View' is selected."
