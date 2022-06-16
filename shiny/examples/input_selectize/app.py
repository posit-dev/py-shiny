from shiny import *

app_ui = ui.page_fluid(
    ui.input_selectize(
        "state",
        "Choose a state:",
        {
            "East Coast": {"NY": "NY", "NJ": "NJ", "CT": "CT"},
            "West Coast": {"WA": "WA", "OR": "OR", "CA": "CA"},
            "Midwest": {"MN": "MN", "WI": "WI", "IA": "IA"},
        },
        multiple=True,
    ),
    ui.output_text("value"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    def value():
        return "You choose: " + str(input.state())


app = App(app_ui, server)
