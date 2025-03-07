from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Basic Numeric Input"),
            ui.input_numeric(id="basic", label="Basic numeric input", value=10),
            ui.output_text("basic_value"),
        ),
        ui.card(
            ui.card_header("With Min/Max"),
            ui.input_numeric(
                id="with_min_max",
                label="With min and max values",
                value=5,
                min=0,
                max=10,
            ),
            ui.output_text("minmax_value"),
        ),
        ui.card(
            ui.card_header("With Step Size"),
            ui.input_numeric(
                id="with_step", label="With step size", value=0, min=0, max=100, step=5
            ),
            ui.output_text("step_value"),
        ),
        ui.card(
            ui.card_header("With Custom Width"),
            ui.input_numeric(
                id="with_width", label="With custom width", value=42, width="200px"
            ),
            ui.output_text("width_value"),
        ),
        width=1 / 2,
    )
)


def server(input, output, session):
    @output
    @render.text
    def basic_value():
        return f"Current value: {input.basic()}"

    @output
    @render.text
    def minmax_value():
        return f"Current value: {input.with_min_max()}"

    @output
    @render.text
    def step_value():
        return f"Current value: {input.with_step()}"

    @output
    @render.text
    def width_value():
        return f"Current value: {input.with_width()}"


app = App(app_ui, server)
