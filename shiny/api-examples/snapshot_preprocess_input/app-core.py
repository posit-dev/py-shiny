from shiny import App, Inputs, Outputs, Session, render, ui
from shiny.testmode import snapshot_preprocess_input

app_ui = ui.page_fluid(
    ui.input_text("secret", "Secret", value="hunter2"),
    ui.output_text_verbatim("shout"),
)


def server(input: Inputs, output: Outputs, session: Session):
    # Scrub the sensitive value from test-mode snapshots; the live input value
    # is untouched. Has no effect unless test mode is enabled
    # (`App(test_mode=True)` or `SHINY_TESTMODE=1`), so the call can be left in
    # production code.
    snapshot_preprocess_input("secret", lambda value: "<redacted>")

    @render.text
    def shout() -> str:
        return str(input.secret()).upper()


app = App(app_ui, server)
