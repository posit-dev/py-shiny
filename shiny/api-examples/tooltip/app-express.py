from icons import question_circle_fill

from shiny.express import ui

with ui.tooltip(id="btn_tooltip"):
    ui.input_action_button("btn", "A button", class_="mt-3")

    "A message"

with ui.card(class_="mt-3"):
    with ui.card_header():
        with ui.tooltip(placement="right", id="card_tooltip"):
            ui.span("Card title ", question_circle_fill)
            "Additional info"

    "Card body content..."
