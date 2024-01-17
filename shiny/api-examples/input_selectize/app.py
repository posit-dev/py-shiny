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
        "state",
        "Selectize Options",
        states,
        multiple=True,
        options=(
            {
                "placeholder": "Enter text",
                "render": ui.JS(
                    '{option: function(item, escape) {return "<div><strong>Select " + item.label + "</strong></div>";}}'
                ),
                "create": True,
            }
        ),
    ),
    ui.input_selectize(
        "state",
        "Selectize plugins",
        states,
        multiple=True,
        options={"plugins": ["clear_button", "remove_button"]},
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def value():
        return "You choose: " + str(input.state())


app = App(app_ui, server)
