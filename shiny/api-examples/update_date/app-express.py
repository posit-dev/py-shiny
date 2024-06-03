from datetime import date, timedelta

from shiny import reactive
from shiny.express import input, ui

ui.input_slider("n", "Day of month", min=1, max=30, value=10)
ui.input_date("inDate", "Input date")


@reactive.effect
def _():
    d = date(2013, 4, input.n())
    ui.update_date(
        "inDate",
        label="Date label " + str(input.n()),
        value=d,
        min=d - timedelta(days=3),
        max=d + timedelta(days=3),
    )
