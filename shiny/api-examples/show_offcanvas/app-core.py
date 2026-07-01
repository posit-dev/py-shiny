from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("show_btn", "Show panel"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.show_btn)
    def _():
        ui.show_offcanvas(
            ui.offcanvas(
                ui.p("This panel was inserted dynamically by the server."),
                title="Server Panel",
                placement="left",
            )
        )


app = App(app_ui, server=server)
