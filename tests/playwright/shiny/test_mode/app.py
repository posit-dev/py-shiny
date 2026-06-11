from shiny import (
    App,
    Inputs,
    Outputs,
    Session,
    export_test_values,
    reactive,
    render,
    ui,
)

app_ui = ui.page_fluid(
    ui.input_text("name", "Name", value="abc"),
    ui.input_slider("n", "N", min=0, max=100, value=20),
    ui.output_text_verbatim("double_txt"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    def doubled() -> int:
        return int(input.n()) * 2

    @render.text
    def double_txt() -> str:
        return f"doubled = {doubled()}"

    # Surface an internal reactive value in the test-mode snapshot.
    export_test_values(doubled=doubled)


# `test_mode=True` is intentional: it exercises the `App(test_mode=)` constructor
# path even though the test fixtures also enable test mode globally.
app = App(app_ui, server, test_mode=True)
