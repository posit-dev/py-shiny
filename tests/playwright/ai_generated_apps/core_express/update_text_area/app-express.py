from shiny import reactive
from shiny.express import input, render, ui

ui.page_opts(title="Text Area Update Demo", fillable=True)

# Initial text area with a card wrapper for better visual organization
with ui.card():
    ui.card_header("Text Area Demo")
    ui.input_text_area(
        id="textarea",
        label="Sample Text Area",
        value="Initial text",
        placeholder="Enter your text here",
        rows=5,
        height="200px",
    )

# Controls for updating text area in a separate card
with ui.card():
    ui.card_header("Control Panel")
    with ui.layout_column_wrap(width=1 / 2):
        ui.input_text("new_label", "New Label", value="Updated Label")
        ui.input_text("new_value", "New Value", value="Updated text content")
        ui.input_text(
            "new_placeholder", "New Placeholder", value="Updated placeholder text"
        )
        ui.input_action_button("update", "Update Text Area", class_="btn-primary")

# Display current values for verification
with ui.card():
    ui.card_header("Current Values")

    @render.text
    def show_values():
        return f"""
        Current Label: {input.new_label()}
        Current Value: {input.new_value()}
        Current Placeholder: {input.new_placeholder()}
        """


# Effect to update the text area when the button is clicked
@reactive.effect
@reactive.event(input.update)
def _():
    ui.update_text_area(
        id="textarea",
        label=input.new_label(),
        value=input.new_value(),
        placeholder=input.new_placeholder(),
    )
