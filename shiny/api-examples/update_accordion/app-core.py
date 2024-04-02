from shiny import App, Inputs, Outputs, Session, reactive, ui

items = [
    ui.accordion_panel(f"Section {letter}", f"Some narrative for section {letter}")
    for letter in "ABCDE"
]

app_ui = ui.page_fluid(
    ui.input_action_button("set_acc", "Only open sections A,C,E", class_="mt-3 mb-3"),
    # Provide an id to create a shiny input binding
    ui.accordion(*items, id="acc", open=["Section B", "Section D"], multiple=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.set_acc)
    def _():
        ui.update_accordion("acc", show=["Section A", "Section C", "Section E"])


app = App(app_ui, server)
