from shiny import render, ui
from shiny.express import input, layout

layout.set_page(layout.page_sidebar(title="PageTitle"))

with layout.sidebar(id="sidebar", title="SidebarTitle"):
    "Sidebar Content"

with layout.card():
    ui.input_slider("a", "A", 1, 100, 50)

    @render.text
    def txt():
        return input.a()

