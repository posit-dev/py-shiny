from datetime import datetime

from dateutil.relativedelta import relativedelta

from shiny import App, Inputs, Outputs, Session, ui

min_date = datetime.now()
max_date = min_date + relativedelta(days=10)

# Our input requires strings to be in the format "YYYY-MM-DD"
str_min = min_date.strftime("%Y-%m-%d")
str_max = max_date.strftime("%Y-%m-%d")

ui = ui.page_fluid(
    ui.input_date(
        "start_date_picker",
        "Date Type Input:",
        value=max_date,
        min=min_date,
        max=max_date,
        format="dd.mm.yyyy",
        language="en",
    ),
    ui.input_date(
        "str_date_picker",
        "String Type Input:",
        value=str_max,
        min=str_min,
        max=str_max,
        format="dd-mm-yyyy",
        language="en",
    ),
    ui.input_date(
        "none_date_picker",
        "None Type Input:",
        value=None,
        min=None,
        max=None,
        format="dd-mm-yyyy",
        language="en",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(ui, server, debug=True)
