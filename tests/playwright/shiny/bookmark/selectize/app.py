from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, render, ui


def app_ui(request: Request):
    return ui.page_fluid(
        ui.input_selectize(
            "single", "Single", choices=["Day", "Week", "Month"], selected="Month"
        ),
        ui.input_selectize(
            "multiple", "Multiple", choices=["Day", "Week", "Month"], multiple=True
        ),
        ui.output_code("single_value"),
        ui.output_code("multiple_value"),
    )


def server(input: Inputs, output: Outputs, session: Session):
    @render.code
    def single_value():
        return str(input.single())

    @render.code
    def multiple_value():
        return str(input.multiple())


app = App(app_ui, server, bookmark_store="url")
