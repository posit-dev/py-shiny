from datetime import date

from shiny.express import ui

# Default start and end is the current date in the client's time zone
ui.input_date_range("daterange1", "Date range:")
# Set start and end dates
ui.input_date_range(
    "daterange2", "Set start and end date:", start="2001-01-01", end="2010-12-31"
)
# Start and end are always specified in yyyy-mm-dd, even if the display
# format is different
ui.input_date_range(
    "daterange3",
    "Min, max, start, and end dates are set with custom format and separator:",
    start="2001-01-01",
    end="2010-12-31",
    min="2001-01-01",
    max="2012-12-21",
    format="mm/dd/yy",
    separator=" - ",
)
# Pass in Date objects
ui.input_date_range(
    "daterange4",
    "Default start and end use date objects:",
    start=date(2001, 1, 1),
    end=date(2010, 12, 31),
)
# Use different language and different first day of week
ui.input_date_range(
    "daterange5",
    "Language is German and we starts on Monday:",
    language="de",
    weekstart=1,
)
# Start with decade view instead of default month view
ui.input_date_range(
    "daterange6", "Start Date picker in Decade view:", startview="decade"
)
# Set width of the daterange field
ui.input_date_range("daterange7", "Set width of text input:", width="600px")
# Set autoclose to false
ui.input_date_range("daterange8", "Auto close is disabled:", autoclose=False)
