from shiny import render
from shiny.express import input, ui

ui.page_opts(title="PageTitle")

with ui.sidebar(id="sidebar", title="SidebarTitle"):
    "Sidebar Content"

with ui.card(id="card"):
    ui.input_slider("a", "A", 1, 100, 50)

    @render.code
    def txt():
        return input.a()
