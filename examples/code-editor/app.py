from pathlib import Path
from typing import get_args

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.ui._input_code_editor import SUPPORTED_LANGUAGES as languages
from shiny.ui._input_code_editor_bundle import CodeEditorTheme

# Load sample code snippets into a dictionary
examples_dir = Path(__file__).parent / "examples"
sample_code: dict[str, str] = {}

for file_path in examples_dir.iterdir():
    if file_path.is_file():
        language = file_path.stem
        sample_code[language] = file_path.read_text()


# Available themes
themes = list(get_args(CodeEditorTheme))

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text("label", "Label:", value="Code Editor"),
        ui.input_select(
            "language",
            "Language:",
            choices=languages,
            selected="python",
        ),
        ui.input_action_button(
            "load_sample",
            "Load Sample Code",
            class_="btn-secondary btn-sm w-100 mb-2",
        ),
        ui.input_action_button(
            "clear_code",
            "Clear Editor",
            class_="btn-warning btn-sm w-100 mb-2",
        ),
        ui.input_select(
            "theme_light",
            "Light Theme:",
            choices=themes,
            selected="github-light",
        ),
        ui.input_select(
            "theme_dark",
            "Dark Theme:",
            choices=themes,
            selected="github-dark",
        ),
        ui.p(
            ui.input_dark_mode(id="dark_mode", mode="light"),
            " ",
            ui.input_action_link(
                "toggle_dark_mode",
                "Toggle Theme",
            ),
            class_="text-end small",
        ),
        ui.input_checkbox("read_only", "Read Only", value=False),
        ui.input_checkbox("line_numbers", "Line Numbers", value=True),
        ui.input_checkbox("word_wrap", "Word Wrap", value=False),
        ui.input_slider("tab_size", "Tab Size:", min=2, max=8, value=4, step=1),
        ui.input_radio_buttons(
            "indentation",
            "Indentation:",
            choices={"space": "Spaces", "tab": "Tabs"},
            selected="space",
            inline=True,
        ),
        width=300,
        title="Editor Controls",
        gap="0.5rem",
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Code Editor"),
            ui.card_body(
                ui.p(
                    "This editor supports syntax highlighting, line numbers, word wrap, and more. ",
                    "Try pressing ",
                    ui.tags.kbd("Ctrl/Cmd+Enter"),
                    " to submit the code.",
                ),
                ui.input_code_editor(
                    "code",
                    value="import pandas as pd\n\n# Sample Python code\ndata = pd.DataFrame({\n    'x': [1, 2, 3, 4, 5],\n    'y': [2, 4, 6, 8, 10]\n})\n\nprint(data.describe())",
                    label="Code Editor",
                    language="python",
                    line_numbers=True,
                    word_wrap=False,
                    fill=True,
                ),
            ),
        ),
        ui.layout_columns(
            ui.navset_card_underline(
                ui.nav_panel("Value", ui.output_text_verbatim("code_output")),
                ui.nav_panel("Settings", ui.output_text_verbatim("editor_info")),
                title="Editor Info",
            ),
            ui.card(
                ui.card_header("Features & Keyboard Shortcuts"),
                ui.card_body(
                    ui.tags.ul(
                        ui.tags.li(
                            ui.tags.kbd("Ctrl/Cmd+Enter"),
                            " - Submit code (triggers reactive update)",
                        ),
                        ui.tags.li(ui.tags.kbd("Ctrl/Cmd+Z"), " - Undo"),
                        ui.tags.li(ui.tags.kbd("Ctrl/Cmd+Shift+Z"), " - Redo"),
                        ui.tags.li(ui.tags.kbd("Tab"), " - Indent selection"),
                        ui.tags.li(ui.tags.kbd("Shift+Tab"), " - Dedent selection"),
                        ui.tags.li("Copy button in top-right corner"),
                        ui.tags.li("Automatic light/dark theme switching"),
                        ui.tags.li("Update on blur (when editor loses focus)"),
                    ),
                ),
            ),
            col_widths=12,
        ),
    ),
    title="Code Editor Demo",
    class_="bslib-page-dashboard",
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.label)
    def _():
        ui.update_code_editor("code", label=input.label())

    @reactive.effect
    @reactive.event(input.language)
    def _():
        language = input.language()
        # Resolve aliases for checking sample availability
        resolved_lang = {
            "plain": "markdown",
            "html": "markup",
        }.get(language, language)

        # Update button disabled state based on sample availability
        has_sample = resolved_lang in sample_code
        ui.update_action_button(
            "load_sample",
            disabled=not has_sample,
        )
        ui.update_code_editor("code", language=language)

    @reactive.effect
    @reactive.event(input.theme_light)
    def _():
        ui.update_code_editor("code", theme_light=input.theme_light())

    @reactive.effect
    @reactive.event(input.theme_dark)
    def _():
        ui.update_code_editor("code", theme_dark=input.theme_dark())

    @reactive.effect
    @reactive.event(input.read_only)
    def _():
        ui.update_code_editor("code", read_only=input.read_only())

    @reactive.effect
    @reactive.event(input.line_numbers)
    def _():
        ui.update_code_editor("code", line_numbers=input.line_numbers())

    @reactive.effect
    @reactive.event(input.word_wrap)
    def _():
        ui.update_code_editor("code", word_wrap=input.word_wrap())

    @reactive.effect
    @reactive.event(input.tab_size)
    def _():
        ui.update_code_editor("code", tab_size=input.tab_size())

    @reactive.effect
    @reactive.event(input.indentation)
    def _():
        ui.update_code_editor("code", indentation=input.indentation())

    @reactive.effect
    @reactive.event(input.load_sample)
    def _():
        language = input.language()
        # Resolve aliases
        resolved_lang = {
            "plain": "markdown",
            "html": "markup",
        }.get(language, language)

        sample = sample_code.get(resolved_lang)
        if sample is not None:
            ui.update_code_editor("code", value=sample, language=language)

    @reactive.effect
    @reactive.event(input.clear_code)
    def _():
        ui.update_code_editor("code", value="")

    @reactive.effect
    @reactive.event(input.toggle_dark_mode)
    def _():
        current_mode = input.dark_mode()
        new_mode = "dark" if current_mode == "light" else "light"
        ui.update_dark_mode(new_mode)

    @render.text
    def code_output():
        code = input.code()
        if code is None or code == "":
            return "[Editor is empty]"
        return code

    @render.text
    def editor_info():
        code = input.code()
        if code is None:
            code = ""

        lines = len(code.split("\n"))
        chars = len(code)

        return "\n".join(
            [
                f"Language: {input.language()}",
                f"Lines: {lines}",
                f"Characters: {chars}",
                f"Read Only: {input.read_only()}",
                f"Line Numbers: {input.line_numbers()}",
                f"Word Wrap: {input.word_wrap()}",
                f"Tab Size: {input.tab_size()}",
                f"Indentation: {input.indentation()}",
            ]
        )


app = App(app_ui, server)
