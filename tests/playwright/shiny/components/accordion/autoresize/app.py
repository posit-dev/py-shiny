from shiny.express import render, ui

with ui.navset_card_tab(id="tab"):

    with ui.nav_panel("Tab 1"):
        "Tab 1 content"
    with ui.nav_panel("Text Area"):
        ui.input_text_area(
            id="test_text_area",
            label="A text area input",
            autoresize=True,
            value="How can this UI code be tweaked\n"
            "such that this multiline string\n"
            "makes the Text Area Input object\n"
            "resize itself event though it lives\n"
            "inside an Accordion element?",
        )

        ui.input_text_area(
            id="test_text_area2",
            label="A second text area input",
            autoresize=True,
            value="How can this UI code be tweaked\n"
            "such that this multiline string\n"
            "makes the Text Area Input object\n"
            "resize itself event though it lives\n"
            "inside an Accordion element?",
            rows=4,
        )


@render.code
def text():
    return "Loaded"
