import pandas as pd

from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.h2("Shiny for Python Demo with Multiple Inputs and Data Grid"),
    ui.layout_sidebar(
        ui.sidebar(  # Use ui.sidebar()
            ui.input_action_button("action_button", "Click me!"),
            ui.input_checkbox("checkbox", "Check this box"),
            ui.input_date("date_selector", "Select a date"),
            ui.input_numeric("numeric_input", "Enter a number", 10),
            ui.input_radio_buttons(
                "radio_buttons", "Choose one:", ["Option A", "Option B", "Option C"]
            ),
            ui.input_switch("switch", "Turn on/off"),
        ),
        ui.h3("Output Values"),
        ui.output_text("action_button_value"),
        ui.output_text("checkbox_value"),
        ui.output_text("date_selector_value"),
        ui.output_text("numeric_input_value"),
        ui.output_text("radio_buttons_value"),
        ui.output_text("switch_value"),
        ui.h3("Data Grid Output"),
        ui.output_data_frame("data_grid"),
    ),
)


def server(input, output, session):
    @render.text
    def action_button_value():
        return f"Action Button clicked: {input.action_button()}"

    @render.text
    def checkbox_value():
        return f"Checkbox checked: {input.checkbox()}"

    @render.text
    def date_selector_value():
        return f"Selected date: {input.date_selector()}"

    @render.text
    def numeric_input_value():
        return f"Numeric Input value: {input.numeric_input()}"

    @render.text
    def radio_buttons_value():
        return f"Selected Radio Button: {input.radio_buttons()}"

    @render.text
    def switch_value():
        return f"Switch status: {input.switch()}"

    @render.data_frame
    def data_grid():
        data = {
            "Input": [
                "Action Button",
            ],
            "Value": [
                input.action_button(),
            ],
        }
        df = pd.DataFrame(data)
        return render.DataGrid(df)


app = App(app_ui, server)
