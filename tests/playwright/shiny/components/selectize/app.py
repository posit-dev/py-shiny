from shiny import App, Inputs, Outputs, Session, module, reactive, ui


@module.ui
def reprex_selectize_ui():
    return ui.input_selectize("x", "Server side selectize", choices=[], multiple=True)


@module.server
def reprex_selectize_server(
    input: Inputs, output: Outputs, session: Session, starting_value: int = 0
):
    @reactive.effect
    def _():
        ui.update_selectize(
            "x",
            choices=[f"Foo {i}" for i in range(3)],
            server=False,
            options={"placeholder": "Search"},
        )


app_ui = ui.page_fluid(reprex_selectize_ui("reprex_selectize"))


def server(input: Inputs, output: Outputs, session: Session):
    reprex_selectize_server("reprex_selectize")


app = App(app_ui, server, debug=True)
