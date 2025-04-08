from shiny import App, render, ui

# Define the UI
app_ui = ui.page_fluid(
    # Card containing all elements
    ui.card(
        ui.card_header("Checkbox Demo"),
        # Basic checkbox with default value (False)
        ui.input_checkbox(id="basic", label="Basic checkbox"),
        # Checkbox with initial value set to True
        ui.input_checkbox(
            id="preset_value", label="Checkbox with preset value", value=True
        ),
        # Checkbox with custom width
        ui.input_checkbox(
            id="custom_width",
            label="Checkbox with custom width (300px)",
            value=False,
            width="300px",
        ),
        # Output UI for checkbox values
        ui.output_ui("checkbox_values"),
    )
)


# Define the server
def server(input, output, session):
    @output
    @render.ui
    def checkbox_values():
        return ui.tags.div(
            ui.tags.p(f"Basic checkbox value: {input.basic()}"),
            ui.tags.p(f"Preset value checkbox: {input.preset_value()}"),
            ui.tags.p(f"Custom width checkbox: {input.custom_width()}"),
        )


# Create the app
app = App(app_ui, server)
