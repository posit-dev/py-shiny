import starlette.responses

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.markdown(
        """
        ## Sticky load balancing test

        The purpose of this app is to determine if HTTP requests made by the client are
        correctly routed back to the same Python process where the session resides. It
        is only useful for testing deployments that load balance traffic across more
        than one Python process.

        If this test fails, it means that sticky load balancing is not working, and
        certain Shiny functionality (like file upload/download or server-side selectize)
        are likely to randomly fail.
        """
    ),
    ui.tags.div(
        {"class": "card"},
        ui.tags.div(
            {"class": "card-body font-monospace"},
            ui.tags.div("Attempts: ", ui.tags.span("0", id="count")),
            ui.tags.div("Status: ", ui.tags.span(id="status")),
            ui.output_ui("out"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.ui
    def out():
        # Register a dynamic route for the client to try to connect to.
        # It does nothing, just the 200 status code is all that the client
        # will care about.
        url = session.dynamic_route(
            "test",
            lambda req: starlette.responses.PlainTextResponse(
                "OK", headers={"Cache-Control": "no-cache"}
            ),
        )

        # Send JS code to the client to repeatedly hit the dynamic route.
        # It will succeed if and only if we reach the correct Python
        # process.
        return ui.tags.script(
            f"""
            const url = "{url}";
            const count_el = document.getElementById("count");
            const status_el = document.getElementById("status");
            let count = 0;
            async function check_url() {{
                count_el.innerHTML = ++count;
                try {{
                    const resp = await fetch(url);
                    if (!resp.ok) {{
                        status_el.innerHTML = "Failure!";
                        return;
                    }} else {{
                        status_el.innerHTML = "In progress";
                    }}
                }} catch(e) {{
                    status_el.innerHTML = "Failure!";
                    return;
                }}

                if (count === 100) {{
                    status_el.innerHTML = "Test complete";
                    return;
                }}

                setTimeout(check_url, 10);
            }}
            check_url();
            """
        )


app = App(app_ui, server)
