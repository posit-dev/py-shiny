from data import adjectives, animals, dark_color, light_color

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fixed(
    ui.h1("Toggle Sidebars"),
    ui.div(
        ui.input_action_button("open_all", "Show all", class_="me-1 mb-1"),
        ui.input_action_button("close_all", "Close all", class_="mb-1"),
        ui.tags.br(),
        ui.input_action_button("toggle_outer", "Toggle outer", class_="me-1"),
        ui.input_action_button("toggle_inner", "Toggle inner"),
        class_="my-2",
    ),
    ui.layout_sidebar(
        ui.sidebar(
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
        ui.layout_sidebar(
            ui.sidebar(
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
    @render.ui
    def ui_content():
        return f"Hello, {input.adjective()} {input.animal()}!"

    @reactive.effect
    @reactive.event(input.open_all)
    def _():
        ui.update_sidebar("sidebar_inner", show=True)
        ui.update_sidebar("sidebar_outer", show=True)

    @reactive.effect
    @reactive.event(input.close_all)
    def _():
        ui.update_sidebar("sidebar_inner", show=False)
        ui.update_sidebar("sidebar_outer", show=False)

    @reactive.effect
    @reactive.event(input.toggle_inner)
    def _():
        ui.update_sidebar("sidebar_inner", show=not input.sidebar_inner())

    @reactive.effect
    @reactive.event(input.toggle_outer)
    def _():
        ui.update_sidebar("sidebar_outer", show=not input.sidebar_outer())


app = App(app_ui, server)
