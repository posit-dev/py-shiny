from starlette.requests import Request
from starlette.responses import JSONResponse

from shiny import reactive
from shiny.express import input, session, ui

ui.input_action_button("serve", "Click to serve")

ui.div(id="messages")


@reactive.effect
@reactive.event(input.serve)
def _():
    async def my_handler(request: Request) -> JSONResponse:
        return JSONResponse({"n_clicks": input.serve()}, status_code=200)

    path = session.dynamic_route("my_handler", my_handler)

    print("Serving at: ", path)

    ui.insert_ui(
        ui.tags.script(
            f"""
            fetch('{path}')
                .then(r => r.json())
                .then(x => {{ $('#messages').text(`Clicked ${{x.n_clicks}} times`); }});
            """
        ),
        selector="body",
    )
