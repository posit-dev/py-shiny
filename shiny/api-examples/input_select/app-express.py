from shiny.express import input, render, ui

ui.input_select(
    "state",
    "Choose a state:",
    {
        "East Coast": {"NY": "New York", "NJ": "New Jersey", "CT": "Connecticut"},
        "West Coast": {"WA": "Washington", "OR": "Oregon", "CA": "California"},
        "Midwest": {"MN": "Minnesota", "WI": "Wisconsin", "IA": "Iowa"},
    },
)


@render.text
def value():
    return "You choose: " + str(input.state())
