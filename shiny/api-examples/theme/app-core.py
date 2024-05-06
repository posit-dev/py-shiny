from pathlib import Path

from shiny import App, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_numeric("n", "N", min=0, max=100, value=20),
        ui.input_slider("m", "M", min=0, max=100, value=50),
        ui.input_selectize("letter", "Letter", choices="A B C D E".split()),
        title="Parameters",
    ),
    ui.h2("Output"),
    ui.output_text_verbatim("txt"),
    ui.markdown(
        """
**AI-generated filler text.** In the world of exotic fruits, the durian stands out with its spiky exterior and strong odor. Despite its divisive smell, many people are drawn to its rich, creamy texture and unique flavor profile. This tropical fruit is often referred to as the "king of fruits" in various Southeast Asian countries.

Durians are known for their large size and thorn-covered husk, which requires careful handling. The flesh inside can vary in color from pale yellow to deep orange, with a custard-like consistency that melts in your mouth. Some describe its taste as a mix of sweet, savory, and creamy, while others find it overpowering and pungent.
"""
    ),
    title="Theme Example",
    theme=ui.Theme("shiny")
    .add_defaults(
        headings_color="red",
        bar_color="purple",
        select_color_text="green",
        bslib_dashboard_design=True,
    )
    .add_mixins("$bslib-sidebar-bg: $gray-200;")
    .add_rules(
        """
        strong { color: $primary; }
        .sidebar-title { color: $danger; }
        """
    ),
    # theme="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css",
    # theme=Path(__file__).parent / "css" / "bootswatch-minty.min.css",
)


def server(input, output, session):
    @render.text
    def txt():
        return f"n*2 is {input.n() * 2}"


app = App(app_ui, server)
