from datetime import date

from shiny import App, Inputs, Outputs, Session, ui

app_ui = ui.page_fluid(
    ui.input_date_range(
        "daterange1", "Date range:", start="2001-01-01", end="2010-12-31"
    ),
    # Default start and end is the current date in the client's time zone
    ui.input_date_range("daterange2", "Date range:"),
    # start and end are always specified in yyyy-mm-dd, even if the display
    # format is different
    ui.input_date_range(
        "daterange3",
        "Date range:",
        start="2001-01-01",
        end="2010-12-31",
        min="2001-01-01",
        max="2012-12-21",
        format="mm/dd/yy",
        separator=" - ",
    ),
    # Pass in Date objects
    ui.input_date_range(
        "daterange4", "Date range:", start=date(2001, 1, 1), end=date(2010, 12, 31)
    ),
    # Use different language and different first day of week
    ui.input_date_range("daterange5", "Date range:", language="de", weekstart=1),
    # Start with decade view instead of default month view
    ui.input_date_range("daterange6", "Date range:", startview="decade"),
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)
