from icons import question_circle_fill

from shiny import App, ui

app_ui = ui.page_fluid(
    ui.tooltip(
        ui.input_action_button("btn", "A button", class_="mt-3"),
        "A message",
        id="btn_tooltip",
    ),
    ui.hr(),
    ui.card(
        ui.card_header(
            ui.tooltip(
                ui.span("Card title ", question_circle_fill),
                "Additional info",
                placement="right",
                id="card_tooltip",
            ),
        ),
        "Card body content...",
    ),
)


app = App(app_ui, server=None)
