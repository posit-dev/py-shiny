from datetime import date

from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.h2("Date Input Parameters Demo"),
    # Basic date input example
    ui.div(
        ui.input_date("date1", "Default date input:", value="2024-01-01"),
        ui.output_text("selected_date1"),
    ),
    ui.br(),
    # Date input with minimum and maximum date constraints
    ui.div(
        ui.input_date(
            "date2",
            "Date input with min/max:",
            value=date(2024, 1, 1),  # Using a date object instead of string
            min="2024-01-01",
            max="2024-12-31",
        ),
        ui.output_text("selected_date2"),
    ),
    ui.br(),
    # Date input with custom date format
    ui.div(
        ui.input_date(
            "date3",
            "Custom format (mm/dd/yy):",
            value="2024-01-01",
            format="mm/dd/yy",  # Changes how date is displayed
        ),
        ui.output_text("selected_date3"),
    ),
    ui.br(),
    # Date input that opens to decade view instead of default month view
    ui.div(
        ui.input_date(
            "date4", "Start in decade view:", value="2024-01-01", startview="decade"
        ),
        ui.output_text("selected_date4"),
    ),
    ui.br(),
    # Date input with week starting on Monday (1) instead of Sunday (0)
    ui.div(
        ui.input_date(
            "date5", "Week starts on Monday:", value="2024-01-01", weekstart=1
        ),
        ui.output_text("selected_date5"),
    ),
    ui.br(),
    # Date input with German language localization
    ui.div(
        ui.input_date("date6", "German language:", value="2024-01-01", language="de"),
        ui.output_text("selected_date6"),
    ),
    ui.br(),
    # Date input with custom width
    ui.div(
        ui.input_date("date7", "Custom width:", value="2024-01-01", width="400px"),
        ui.output_text("selected_date7"),
    ),
    # Date input where calendar doesn't auto-close after selection
    ui.div(
        ui.input_date(
            "date8", "Autoclose disabled:", value="2024-01-01", autoclose=False
        ),
        ui.output_text("selected_date8"),
    ),
    ui.br(),
    # Date input with specific dates disabled/unavailable for selection
    ui.div(
        ui.input_date(
            "date9",
            "Specific dates disabled:",
            value="2024-01-01",
            datesdisabled=["2024-01-15", "2024-01-16", "2024-01-17"],
        ),
        ui.output_text("selected_date9"),
    ),
    ui.br(),
    # Date input with weekend days disabled/unavailable for selection
    ui.div(
        ui.input_date(
            "date10",
            "Weekends disabled:",
            value="2024-01-01",
            daysofweekdisabled=[0, 6],  # 0 = Sunday, 6 = Saturday
        ),
        ui.output_text("selected_date10"),
    ),
)


def server(input, output, session):
    # Server functions to display the selected date for each input
    @render.text
    def selected_date1():
        return f"Selected date: {input.date1()}"

    @render.text
    def selected_date2():
        return f"Selected date: {input.date2()}"

    @render.text
    def selected_date3():
        return f"Selected date: {input.date3()}"

    @render.text
    def selected_date4():
        return f"Selected date: {input.date4()}"

    @render.text
    def selected_date5():
        return f"Selected date: {input.date5()}"

    @render.text
    def selected_date6():
        return f"Selected date: {input.date6()}"

    @render.text
    def selected_date7():
        return f"Selected date: {input.date7()}"

    @render.text
    def selected_date8():
        return f"Selected date: {input.date8()}"

    @render.text
    def selected_date9():
        return f"Selected date: {input.date9()}"

    @render.text
    def selected_date10():
        return f"Selected date: {input.date10()}"


# Create and define the Shiny app with UI and server components
app = App(app_ui, server)
