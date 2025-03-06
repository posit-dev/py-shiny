from datetime import date

from shiny.express import input, render, ui

# Add some descriptive text
ui.h2("Date Range Input Example")
ui.markdown(
    """
This example demonstrates a date range input with various customization options:
- Custom date format (mm/dd/yyyy)
- Restricted date range (2020-2025)
- Week starting on Monday
- Custom separator
"""
)

with ui.layout_column_wrap():
    # Create a date range input with all possible parameters
    ui.input_date_range(
        id="date_range",
        label="Select Date Range",
        start=date(2023, 1, 1),  # Initial start date
        end=date(2023, 12, 31),  # Initial end date
        min=date(2020, 1, 1),  # Minimum allowed date
        max=date(2025, 12, 31),  # Maximum allowed date
        format="mm/dd/yyyy",  # Display format
        startview="decade",  # Initial view when opened
        weekstart=1,  # Week starts on Monday (0=Sunday, 1=Monday)
        language="en",  # Language for month/day names
        separator=" → ",  # Custom separator between dates
        width="100%",  # Width of the input
        autoclose=True,  # Close the calendar when a date is selected
    )

    # Add a card to display the selected range
    with ui.card():
        ui.card_header("Selected Date Range")

        @render.text
        def selected_range():
            date_range = input.date_range()
            if date_range is None:
                return "No dates selected"

            start, end = date_range
            return f"Start date: {start}\nEnd date: {end}"


# Add some additional information about the selection
@render.ui
def date_info():
    date_range = input.date_range()
    if date_range is None:
        return ui.p("Please select a date range", class_="text-muted")

    start, end = date_range
    days = (end - start).days

    return ui.div(
        ui.p(f"Number of days selected: {days}"),
        ui.p(f"Start day of week: {start.strftime('%A')}"),
        ui.p(f"End day of week: {end.strftime('%A')}"),
        class_="mt-3",
    )
