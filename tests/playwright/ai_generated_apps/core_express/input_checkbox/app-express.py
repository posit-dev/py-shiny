from shiny.express import input, render, ui

with ui.card():
    ui.card_header("Checkbox Demo")

    # Basic checkbox with default value (False)
    ui.input_checkbox(id="basic", label="Basic checkbox")

    # Checkbox with initial value set to True
    ui.input_checkbox(id="preset_value", label="Checkbox with preset value", value=True)

    # Checkbox with custom width
    ui.input_checkbox(
        id="custom_width",
        label="Checkbox with custom width (300px)",
        value=False,
        width="300px",
    )

    # Display the values of all checkboxes
    @render.ui
    def checkbox_values():
        return ui.tags.div(
            ui.tags.p(f"Basic checkbox value: {input.basic()}"),
            ui.tags.p(f"Preset value checkbox: {input.preset_value()}"),
            ui.tags.p(f"Custom width checkbox: {input.custom_width()}"),
        )
