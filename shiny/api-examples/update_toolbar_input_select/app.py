from faicons import icon_svg

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Update Toolbar Input Select Example"),
    ui.p(
        "This example demonstrates updating a toolbar select's label, choices, icon, and selected value when a button is clicked."
    ),
    ui.card(
        ui.card_header(
            ui.toolbar(
                ui.toolbar_input_select(
                    "select", label="Choose", choices=["A", "B", "C"]
                ),
                ui.toolbar_input_button("update_btn", label="Update Select"),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text_verbatim("value"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @output
    @render.text
    def value():
        return str(input.select())

    @reactive.effect
    @reactive.event(input.update_btn)
    def _():
        ui.update_toolbar_input_select(
            "select",
            label="Pick one",
            choices=["New 1", "New 2", "New 3"],
            selected="New 2",
            icon=icon_svg("filter"),
            show_label=True,
        )


app = App(app_ui, server)
