from datetime import datetime

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_text("name", "Name", value="Shiny"),
    ui.output_text_verbatim("greeting"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def greeting() -> str:
        return f"Hello, {input.name()}! It is {datetime.now().isoformat()}."

    # Scrub the nondeterministic timestamp from test-mode snapshots so they
    # diff cleanly; the value sent to the client is untouched. Has no effect
    # unless test mode is enabled (`App(test_mode=True)` or
    # `SHINY_TESTMODE=1`), so the call can be left in production code.
    greeting.snapshot_preprocess(lambda value: value.split(" It is ")[0])


app = App(app_ui, server)
