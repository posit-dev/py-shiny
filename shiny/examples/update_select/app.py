from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.tags.p("The checkbox group controls the select input"),
    ui.input_checkbox_group(
        "inCheckboxGroup", "Input checkbox", ["Item A", "Item B", "Item C"]
    ),
    ui.input_select("inSelect", "Select input", ["Item A", "Item B", "Item C"]),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        x = input.inCheckboxGroup()

        # Can use [] to remove all choices
        if x is None:
            x = []
        elif isinstance(x, str):
            x = [x]

        ui.update_select(
            "inSelect",
            label="Select input label " + str(len(x)),
            choices=x,
            selected=x[len(x) - 1] if len(x) > 0 else None,
        )


app = App(app_ui, server)
