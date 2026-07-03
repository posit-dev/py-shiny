from datetime import datetime

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.testmode import export_test_values

app_ui = ui.page_fluid(
    ui.input_text("name", "Name", value="abc"),
    ui.input_text("secret", "Secret", value="hunter2"),
    ui.input_slider("n", "N", min=0, max=100, value=20),
    ui.output_text_verbatim("double_txt"),
    ui.output_text_verbatim("stamp"),
)


def server(input: Inputs, output: Outputs, session: Session):
    # Scrub a sensitive input out of the test-mode snapshot.
    input.set_snapshot_preprocess("secret", lambda value: "<redacted>")

    @reactive.calc
    def doubled() -> int:
        return int(input.n()) * 2

    @render.text
    def double_txt() -> str:
        return f"doubled = {doubled()}"

    @render.text
    def stamp() -> str:
        return f"time = {datetime.now().isoformat()}"

    # Scrub the nondeterministic timestamp out of the test-mode snapshot.
    stamp.snapshot_preprocess(lambda value: "time = <scrubbed>")

    # Surface an internal reactive value in the test-mode snapshot.
    export_test_values(doubled=doubled)


# `test_mode=True` is intentional: it exercises the `App(test_mode=)` constructor
# path even though the test fixtures also enable test mode globally.
app = App(app_ui, server, test_mode=True)
