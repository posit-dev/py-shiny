from datetime import date
from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.layout_column_wrap(
        ui.div(
            ui.input_date("date1", "Default date input:", value="2024-01-01"),
            ui.output_text("selected_date1"),
        ),
        ui.div(
            ui.input_date(
                "date2",
                "Date input with min/max:",
                value=date(2024, 1, 1),
                min="2024-01-01",
                max="2024-12-31",
            ),
            ui.output_text("selected_date2"),
        ),
        ui.div(
            ui.input_date(
                "date3",
                "Custom format (mm/dd/yy):",
                value="2024-01-01",
                format="mm/dd/yy",
            ),
            ui.output_text("selected_date3"),
        ),
        ui.div(
            ui.input_date(
                "date4", "Start in decade view:", value="2024-01-01", startview="decade"
            ),
            ui.output_text("selected_date4"),
        ),
        ui.div(
            ui.input_date(
                "date5", "Week starts on Monday:", value="2024-01-01", weekstart=1
            ),
            ui.output_text("selected_date5"),
        ),
        ui.div(
            ui.input_date(
                "date6", "German language:", value="2024-01-01", language="de"
            ),
            ui.output_text("selected_date6"),
        ),
        ui.div(
            ui.input_date("date7", "Custom width:", value="2024-01-01", width="400px"),
            ui.output_text("selected_date7"),
        ),
        ui.div(
            ui.input_date(
                "date8", "Autoclose disabled:", value="2024-01-01", autoclose=False
            ),
            ui.output_text("selected_date8"),
        ),
        ui.div(
            ui.input_date(
                "date9",
                "Specific dates disabled:",
                value="2024-01-01",
                datesdisabled=["2024-01-15", "2024-01-16", "2024-01-17"],
            ),
            ui.output_text("selected_date9"),
        ),
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
)


def server(input, output, session):
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


app = App(app_ui, server)
