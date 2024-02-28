from datetime import date

from shiny import App, Inputs, Outputs, Session, ui

app_ui = ui.page_fluid(
    ui.input_date("date1", "Date:", value="2016-02-29"),
    # Default value is the date in client's time zone
    ui.input_date("date2", "Date:"),
    # value is always yyyy-mm-dd, even if the display format is different
    ui.input_date("date3", "Date:", value="2016-02-29", format="mm/dd/yy"),
    # Pass in a Date object
    ui.input_date("date4", "Date:", value=date(2016, 2, 29)),
    # Use different language and different first day of week
    ui.input_date("date5", "Date:", language="ru", weekstart=1),
    # Start with decade view instead of default month view
    ui.input_date("date6", "Date:", startview="decade"),
    # Disable Mondays and Tuesdays.
    ui.input_date("date7", "Date:", daysofweekdisabled=[1, 2]),
    # Disable specific dates.
    ui.input_date(
        "date8",
        "Date:",
        value="2016-02-29",
        datesdisabled=["2016-03-01", "2016-03-02"],
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)
