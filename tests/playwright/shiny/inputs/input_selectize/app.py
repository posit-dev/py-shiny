from shiny import App, Inputs, Outputs, Session, render, ui

states = {
    "East Coast": {"NY": "New York", "NJ": "New Jersey", "CT": "Connecticut"},
    "West Coast": {"WA": "Washington", "OR": "Oregon", "CA": "California"},
    "Midwest": {"MN": "Minnesota", "WI": "Wisconsin", "IA": "Iowa"},
}

state_without_groups = {"NY": "New York", "NJ": "New Jersey", "CT": "Connecticut"}
state_without_keys = ["New York", "New Jersey", "Connecticut"]

app_ui = ui.page_fluid(
    ui.input_selectize(
        "state1",
        "Choose a state:",
        states,
        multiple=True,
    ),
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
        "Single Selectize",
        state_without_groups,
        multiple=False,
        options={"plugins": ["clear_button"]},
    ),
    ui.input_selectize(
        "state4",
        "Simple Selectize",
        state_without_keys,
        multiple=False,
    ),
    ui.hr(),
    ui.output_code("value1"),
    ui.output_code("value2"),
    ui.output_code("value3"),
    ui.output_code("value4"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.code
    def value1():
        return str(input.state1())

    @render.code
    def value2():
        return str(input.state2())

    @render.code
    def value3():
        return str(input.state3())

    @render.code
    def value4():
        return str(input.state4())


app = App(app_ui, server)
