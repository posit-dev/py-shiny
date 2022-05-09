import random

from shiny import *
from htmltools import HTMLDependency
from starlette.responses import JSONResponse
from starlette.requests import Request

app_ui = ui.page_fluid(
    ui.input_action_button("serve", "Click to serve"), ui.div(id="messages")
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect()
    @event(input.serve)
    def _():
        @session.dynamic_route()
        def my_handler(request: Request) -> JSONResponse:
            return JSONResponse({"n_clicks": input.serve()}, status_code=200)

        path = my_handler()
        print("Serving at: ", path)

        ui.insert_ui(
            # TODO: inserting a raw <script> doesn't work here, this might
            # motivation for head_content(dedup=False)
            HTMLDependency(
                name=str(random.randint(0, 1000)),
                version="1.0",
                head=ui.tags.script(
                    f"""
                    fetch('{path}')
                      .then(r => r.json())
                      .then(x => {{ $('#messages').text(`Clicked ${{x.n_clicks}} times`); }});
                    """
                ),
            ),
            selector="head",
        )


app = App(app_ui, server)
