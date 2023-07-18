from pathlib import Path

from shiny import App, ui

css_file = Path(__file__).parent / "css" / "styles.css"

app_ui = ui.page_fluid(
    "Almost before we knew it, we had left the ground!!!",
    ui.include_css(css_file),
    ui.div(
        # Style individual elements with an attribute dictionary.
        {"style": "font-weight: bold"},
        ui.p("Bold text"),
    ),
)

app = App(app_ui, None)
