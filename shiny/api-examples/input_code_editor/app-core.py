from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fillable(
    ui.layout_columns(
        ui.card(
            ui.card_header("Python Code Editor"),
            ui.input_code_editor(
                "code",
                label="Enter Python code:",
                value="def greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('World'))",
                language="python",
                height="200px",
            ),
        ),
        ui.card(
            ui.card_header("Editor Value"),
            ui.output_text_verbatim("value", placeholder=True),
        ),
        col_widths=[6, 6],
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def value():
        return input.code()


app = App(app_ui, server)
