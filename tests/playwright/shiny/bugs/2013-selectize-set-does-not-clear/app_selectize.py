from shiny import App, render, ui
from shiny.session import Inputs, Outputs, Session

app_ui = ui.page_fluid(
    ui.input_selectize(
        "test_selectize",
        "Select",
        ["Choice 1", "Choice 2", "Choice 3", "Choice 4"],
        multiple=True,
    ),
    ui.output_text("test_selectize_output"),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @render.text
    def test_selectize_output():
        return f"Selected: {', '.join(input.test_selectize())}"


app = App(app_ui, server)
