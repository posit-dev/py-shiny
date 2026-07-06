from shiny import App, Inputs, Outputs, Session, reactive, ui

code_samples = {
    "python": "def greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('World'))",
    "r": "greet <- function(name) {\n  paste0('Hello, ', name, '!')\n}\n\nprint(greet('World'))",
    "javascript": "function greet(name) {\n  return `Hello, ${name}!`;\n}\n\nconsole.log(greet('World'));",
}

app_ui = ui.page_fillable(
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "language",
                "Language:",
                choices=["python", "r", "javascript"],
                selected="python",
            ),
            ui.input_switch("read_only", "Read only", value=False),
            ui.input_switch("line_numbers", "Line numbers", value=True),
        ),
        ui.input_code_editor(
            "code",
            label="Code editor:",
            value=code_samples["python"],
            language="python",
        ),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.language)
    def _():
        ui.update_code_editor(
            "code",
            value=code_samples[input.language()],
            language=input.language(),
        )

    @reactive.effect
    @reactive.event(input.read_only)
    def _():
        ui.update_code_editor("code", read_only=input.read_only())

    @reactive.effect
    @reactive.event(input.line_numbers)
    def _():
        ui.update_code_editor("code", line_numbers=input.line_numbers())


app = App(app_ui, server)
