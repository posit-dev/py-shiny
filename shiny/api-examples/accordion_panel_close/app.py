from shiny import App, Inputs, Outputs, Session, reactive, ui

items = [
    ui.accordion_panel(f"Section {letter}", f"Some narrative for section {letter}")
    for letter in "ABCDE"
]

app_ui = ui.page_fluid(
    ui.input_action_button("close_acc", "Close Section C", class_="mt-3 mb-3"),
    ui.accordion(*items, id="acc", multiple=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    @reactive.event(input.close_acc)
    def _():
        ui.accordion_panel_close("acc", "Section C")


app = App(app_ui, server)
