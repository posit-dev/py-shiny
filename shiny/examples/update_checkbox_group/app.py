from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.tags.p("The first checkbox group controls the second"),
    ui.input_checkbox_group(
        "inCheckboxGroup", "Input checkbox", ["Item A", "Item B", "Item C"]
    ),
    ui.input_checkbox_group(
        "inCheckboxGroup2", "Input checkbox 2", ["Item A", "Item B", "Item C"]
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        x = input.inCheckboxGroup()

        # Can also set the label and select items
        ui.update_checkbox_group(
            "inCheckboxGroup2",
            label="Checkboxgroup label " + str(len(x)),
            choices=x,
            selected=x,
        )


app = App(app_ui, server)
