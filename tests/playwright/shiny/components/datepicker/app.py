from datetime import datetime

from dateutil.relativedelta import relativedelta

from shiny import App, Inputs, Outputs, Session, render, ui

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
    ui.output_text("start"),
    ui.input_date(
        "str_date_picker",
        "String Type Input:",
        value=str_max,
        min=str_min,
        max=str_max,
        format="dd-mm-yyyy",
        language="en",
    ),
    ui.output_text("str_format"),
    ui.input_date(
        "none_date_picker",
        "None Type Input:",
        value=None,
        min=None,
        max=None,
        format="dd-mm-yyyy",
        language="en",
    ),
    ui.output_text("none_format"),
    ui.input_date(
        "empty_date_picker",
        "empty Type Input:",
        value="",
        min=None,
        max=None,
        format="dd-mm-yyyy",
        language="en",
    ),
    ui.output_text("empty_format"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def start():
        return "Start Date Picker Value: " + str(input.start_date_picker())

    @render.text
    def str_format():
        return "String Date Picker Value: " + str(input.str_date_picker())

    @render.text
    def none_format():
        return "None Date Picker Value: " + str(input.none_date_picker())

    @render.text
    def empty_format():
        return "Empty Date Picker Value: " + str(input.empty_date_picker())


app = App(ui, server, debug=True)
