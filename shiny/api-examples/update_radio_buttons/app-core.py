from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.tags.p("The first radio button group controls the second"),
    ui.input_radio_buttons(
        "inRadioButtons", "Input radio buttons", ["Item A", "Item B", "Item C"]
    ),
    ui.input_radio_buttons(
        "inRadioButtons2", "Input radio buttons 2", ["Item A", "Item B", "Item C"]
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        x = input.inRadioButtons()

        # Can also set the label and select items
        ui.update_radio_buttons(
            "inRadioButtons2",
            label="Radio buttons label " + x,
            choices=[x],
            selected=x,
        )


app = App(app_ui, server)
