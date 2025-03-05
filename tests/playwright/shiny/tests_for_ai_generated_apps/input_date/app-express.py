from datetime import date
from shiny import reactive
from shiny.express import input, ui, render

with ui.layout_column_wrap():
    # Basic date input
    ui.input_date("date1", "Default date input:", value="2024-01-01")

    @render.text
    def selected_date1():
        return f"Selected date: {input.date1()}"

    # Date input with min and max dates
    ui.input_date(
        "date2",
        "Date input with min/max:",
        value=date(2024, 1, 1),
        min="2024-01-01",
        max="2024-12-31",
    )

    @render.text
    def selected_date2():
        return f"Selected date: {input.date2()}"

    # Date input with custom format
    ui.input_date(
        "date3", "Custom format (mm/dd/yy):", value="2024-01-01", format="mm/dd/yy"
    )

    @render.text
    def selected_date3():
        return f"Selected date: {input.date3()}"

    # Date input with decade view
    ui.input_date(
        "date4", "Start in decade view:", value="2024-01-01", startview="decade"
    )

    @render.text
    def selected_date4():
        return f"Selected date: {input.date4()}"

    # Date input with week starting on Monday
    ui.input_date("date5", "Week starts on Monday:", value="2024-01-01", weekstart=1)

    @render.text
    def selected_date5():
        return f"Selected date: {input.date5()}"

    # Date input with German language
    ui.input_date("date6", "German language:", value="2024-01-01", language="de")

    @render.text
    def selected_date6():
        return f"Selected date: {input.date6()}"

    # Date input with custom width
    ui.input_date("date7", "Custom width:", value="2024-01-01", width="400px")

    @render.text
    def selected_date7():
        return f"Selected date: {input.date7()}"

    # Date input with autoclose disabled
    ui.input_date("date8", "Autoclose disabled:", value="2024-01-01", autoclose=False)

    @render.text
    def selected_date8():
        return f"Selected date: {input.date8()}"

    # Date input with specific dates disabled
    ui.input_date(
        "date9",
        "Specific dates disabled:",
        value="2024-01-01",
        datesdisabled=["2024-01-15", "2024-01-16", "2024-01-17"],
    )

    @render.text
    def selected_date9():
        return f"Selected date: {input.date9()}"

    # Date input with specific days of week disabled
    ui.input_date(
        "date10",
        "Weekends disabled:",
        value="2024-01-01",
        daysofweekdisabled=[0, 6],  # 0 = Sunday, 6 = Saturday
    )

    @render.text
    def selected_date10():
        return f"Selected date: {input.date10()}"
