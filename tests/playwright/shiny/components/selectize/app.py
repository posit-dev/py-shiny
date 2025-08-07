from shiny import App, Inputs, Outputs, Session, module, reactive, ui


@module.ui
def reprex_selectize_ui(label: str):
    return ui.input_selectize("x", label, choices=[], multiple=True)


@module.server
def reprex_selectize_server(
    input: Inputs, output: Outputs, session: Session, server: bool = True
):
    @reactive.effect
    def _():
        ui.update_selectize(
            "x",
            choices=[f"Foo {i}" for i in range(3)],
            server=server,
            options={"placeholder": "Search"},
        )


app_ui = ui.page_fluid(
    reprex_selectize_ui("serverside", "Server"),
    reprex_selectize_ui("clientside", "Client"),
)


def server(input: Inputs, output: Outputs, session: Session):
    reprex_selectize_server("serverside", server=True)
    reprex_selectize_server("clientside", server=False)


app = App(app_ui, server, debug=True)
