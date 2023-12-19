from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.h2("Keyboard Settings"),
    ui.input_switch("auto_capitalization", "Auto-Capitalization", True),
    ui.input_switch("auto_correction", "Auto-Correction", True),
    ui.input_switch("check_spelling", "Check Spelling", True),
    ui.input_switch("smart_punctuation", "Smart Punctuation"),
    ui.output_text_verbatim("preview"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    def preview():
        return f"""Keyboard Settings
==========================
auto_capitalization: {input.auto_capitalization()}
auto_correction: {input.auto_correction()}
check_spelling: {input.check_spelling()}
smart_punctuation: {input.smart_punctuation()}"""


app = App(app_ui, server)
