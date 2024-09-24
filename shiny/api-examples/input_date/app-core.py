from datetime import date

from shiny import App, Inputs, Outputs, Session, ui

app_ui = ui.page_fluid(
    ui.input_date("date1", "Has default date:", value="2016-02-29"),
    # Default value is the date in client's time zone
    ui.input_date("date2", "Client's current date:"),
    # value is always yyyy-mm-dd, even if the display format is different
    ui.input_date("date3", "Format mm/dd/yy:", value="2016-02-29", format="mm/dd/yy"),
    # Pass in a Date object
    ui.input_date("date4", "Default uses date object:", value=date(2016, 2, 29)),
    # Use different language and different first day of week
    ui.input_date(
        "date5",
        "Language is German and the week starts on Monday:",
        language="ru",
        weekstart=1,
    ),
    # Start with decade view instead of default month view
    ui.input_date("date6", "Start Date picker in Decade view:", startview="decade"),
    # Disable Mondays and Tuesdays.
    ui.input_date("date7", "Disable Monday and Tuesday:", daysofweekdisabled=[1, 2]),
    # Disable specific dates.
    ui.input_date(
        "date8",
        "Disable specific dates:",
        value="2016-02-29",
        datesdisabled=["2016-03-01", "2016-03-02"],
    ),
    # Set min and max dates.
    ui.input_date(
        "date9",
        "Set min and max dates:",
        value="2016-02-03",
        min="2016-02-01",
        max="2016-02-29",
    ),
    # Set width of the date field
    ui.input_date("date10", "Set width of text input:", width="600px"),
    # Set autoclose to false
    ui.input_date("date11", "Auto close is disabled:", autoclose=False),
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)
