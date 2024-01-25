from html import escape  # noqa: F401

from shiny import App, Inputs, Outputs, Session, render, ui

states = {
    "East Coast": {"NY": "New York", "NJ": "New Jersey", "CT": "Connecticut"},
    "West Coast": {"WA": "Washington", "OR": "Oregon", "CA": "California"},
    "Midwest": {"MN": "Minnesota", "WI": "Wisconsin", "IA": "Iowa"},
}

app_ui = ui.page_fluid(
    ui.input_selectize(
        "state",
        "Choose a state:",
        states,
        multiple=True,
    ),
    ui.output_text("value"),
    ui.input_selectize(
        "state2",
        "Selectize Options",
        states,
        multiple=True,
        options=(
            {
                "placeholder": "Enter text",
                "render": ui.js_eval(
                    '{option: function(item, escape) {return "<div><strong>Select " + escape(item.label) + "</strong></div>";}}'
                ),
                "create": True,
            }
        ),
    ),
    ui.input_selectize(
        "state3",
        "Selectize plugins",
        states,
        multiple=True,
        options={"plugins": ["clear_button"]},
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def value():
        return "You choose: " + str(input.state())


app = App(app_ui, server)
