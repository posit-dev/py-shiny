from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.testmode import export_test_values

app_ui = ui.page_fluid(
    ui.input_slider("n", "N", min=0, max=100, value=20),
    ui.output_text_verbatim("txt"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    def doubled() -> int:
        return input.n() * 2

    @render.text
    def txt() -> str:
        return f"n * 2 = {doubled()}"

    # Surface the internal reactive value in the test-mode snapshot, under the
    # snapshot's `export` block. Has no effect unless test mode is enabled
    # (`App(test_mode=True)` or `SHINY_TESTMODE=1`), so the call can be left in
    # production code. The `shiny.pytest` app fixtures enable test mode by
    # default, so an end-to-end test can assert on it with the
    # `shiny.playwright.controller.AppTestValues` controller:
    #
    #     app_values = controller.AppTestValues(page)
    #     app_values.expect_export("doubled", 40)
    export_test_values(doubled=doubled)


app = App(app_ui, server)
