import random

from shiny import *
from htmltools import HTMLDependency
from starlette.responses import JSONResponse
from starlette.requests import Request

app_ui = ui.page_fluid(
    ui.input_action_button("serve", "Serve a random value"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect()
    @event(input.serve)
    def _():
        def my_handler(x: dict[str, str], request: Request) -> JSONResponse:
            return JSONResponse(x, status_code=200)

        path = session.serve_object(
            name="my-random-value",
            object={"value": random.randint(0, 100)},
            handler=my_handler,
        )

        print("Serving at: ", path)

        ui.insert_ui(
            # TODO: inserting a raw <script> doesn't work here, this might
            # motivation for head_content(dedup=False)
            HTMLDependency(
                name=str(random.randint(0, 1000)),
                version="1.0",
                head=ui.tags.script(f"fetch('{path}').then(r => r.text()).then(alert)"),
            ),
            selector="head",
        )


app = App(app_ui, server)
