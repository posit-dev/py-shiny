from shiny.express import render, ui

with ui.navset_card_tab(id="tab"):

    with ui.nav_panel("Tab 1"):
        "Tab 1 content"
    with ui.nav_panel("Text Area"):
        ui.input_text_area(
            id="test_text_area",
            label="A text area input",
            autoresize=True,
            value="a\nb\nc\nd\ne",
        )

        ui.input_text_area(
            id="test_text_area2",
            label="A second text area input",
            autoresize=True,
            value="a\nb\nc\nd\ne",
            rows=4,
        )


@render.code
def text():
    return "Loaded"
