"""
Test app for input_code_editor
"""

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fillable(
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Controls"),
            ui.input_action_button("update_value", "Set Python code"),
            ui.input_action_button("update_language", "Change to JavaScript"),
            ui.input_action_button("toggle_read_only", "Toggle read-only"),
            ui.input_action_button("toggle_line_numbers", "Toggle line numbers"),
        ),
        ui.h3("Basic Code Editor"),
        ui.input_code_editor(
            "code",
            label="Python code",
            value="def greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('World'))",
            language="python",
            height="200px",
        ),
        ui.output_text_verbatim("code_value", placeholder=True),
        ui.hr(),
        ui.h3("Read-only Editor"),
        ui.input_code_editor(
            "readonly",
            label="Read-only code",
            value="// This code cannot be edited\nconst x = 42;",
            language="javascript",
            read_only=True,
            height="100px",
        ),
        ui.hr(),
        ui.h3("Markdown Editor (no line numbers)"),
        ui.input_code_editor(
            "markdown",
            label="Markdown text",
            value="# Hello World\n\nThis is **markdown** content.",
            language="markdown",
            height="150px",
        ),
        ui.output_text_verbatim("markdown_value", placeholder=True),
        ui.hr(),
        ui.h3("Custom themed Editor"),
        ui.input_code_editor(
            "themed",
            label="Custom themed",
            value="SELECT * FROM users WHERE id = 1;",
            language="sql",
            theme_light="vs-code-light",
            theme_dark="dracula",
            tab_size=4,
            height="100px",
        ),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    read_only_state = reactive.value(False)  # Match initial editor state
    line_numbers_state = reactive.value(True)

    @render.text
    def code_value():
        return f"Current value:\n{input.code()}"

    @render.text
    def markdown_value():
        return f"Current value:\n{input.markdown()}"

    @reactive.effect
    @reactive.event(input.update_value)
    def _():
        ui.update_code_editor(
            "code",
            value="# Updated from server\nprint('Hello from server!')",
        )

    @reactive.effect
    @reactive.event(input.update_language)
    def _():
        ui.update_code_editor(
            "code",
            value="function hello() {\n  console.log('Hello!');\n}",
            language="javascript",
        )

    @reactive.effect
    @reactive.event(input.toggle_read_only)
    def _():
        read_only_state.set(not read_only_state.get())
        ui.update_code_editor("code", read_only=read_only_state.get())

    @reactive.effect
    @reactive.event(input.toggle_line_numbers)
    def _():
        line_numbers_state.set(not line_numbers_state.get())
        ui.update_code_editor("code", line_numbers=line_numbers_state.get())


app = App(app_ui, server)
