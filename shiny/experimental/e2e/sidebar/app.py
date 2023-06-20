from data import adjectives, animals, dark_color, light_color

from shiny import App, Inputs, Outputs, Session
from shiny import experimental as x
from shiny import reactive, render, ui

app_ui = ui.page_fixed(
    ui.h1("Toggle Sidebars"),
    ui.div(
        ui.input_action_button("open_all", "Show all", class_="me-1"),
        ui.input_action_button("close_all", "Close all", class_="me-2"),
        ui.input_action_button("toggle_outer", "Toggle outer", class_="me-1"),
        ui.input_action_button("toggle_inner", "Toggle inner"),
        class_="my-2",
    ),
    x.ui.layout_sidebar(
        x.ui.sidebar(
            "Outer Sidebar",
            ui.input_select(
                "adjective",
                "Adjective",
                choices=adjectives,
                selected=adjectives[0],
            ),
            id="sidebar_outer",
            width=200,
            bg=dark_color,
            fg="white",
            open="desktop",
            max_height_mobile="300px",
        ),
        x.ui.layout_sidebar(
            x.ui.sidebar(
                "Inner Sidebar",
                ui.input_select(
                    "animal",
                    "Animal",
                    choices=animals,
                    selected=animals[0],
                ),
                id="sidebar_inner",
                # width=200,
                bg=light_color,
                open="desktop",
            ),
            ui.h2("Sidebar Layout"),
            ui.output_ui("ui_content", tabindex=0),
            height=300,
            id="main_inner",
            border=False,
            border_radius=False,
        ),
        id="main_outer",
        class_="p-0",
    ),
    title="bslib | Tests | Dynamic Sidebars",
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @output
    @render.ui
    def ui_content():
        return f"Hello, {input.adjective()} {input.animal()}!"

    @reactive.Effect
    @reactive.event(input.open_all)
    def _():
        x.ui.sidebar_toggle("sidebar_inner", open=True)
        x.ui.sidebar_toggle("sidebar_outer", open=True)

    @reactive.Effect
    @reactive.event(input.close_all)
    def _():
        x.ui.sidebar_toggle("sidebar_inner", open=False)
        x.ui.sidebar_toggle("sidebar_outer", open=False)

    @reactive.Effect
    @reactive.event(input.toggle_inner)
    def _():
        x.ui.sidebar_toggle("sidebar_inner")

    @reactive.Effect
    @reactive.event(input.toggle_outer)
    def _():
        x.ui.sidebar_toggle("sidebar_outer")


app = App(app_ui, server)
