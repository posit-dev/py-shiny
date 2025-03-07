from shiny import App, reactive, render, ui

app_ui = ui.page_fillable(
    # Set page title in the UI
    ui.panel_title("Text Area Update Demo"),
    # Initial text area with a card wrapper
    ui.card(
        ui.card_header("Text Area Demo"),
        ui.input_text_area(
            id="textarea",
            label="Sample Text Area",
            value="Initial text",
            placeholder="Enter your text here",
            rows=5,
            height="200px",
        ),
    ),
    # Controls for updating text area in a separate card
    ui.card(
        ui.card_header("Control Panel"),
        ui.layout_column_wrap(
            ui.input_text("new_label", "New Label", value="Updated Label"),
            ui.input_text("new_value", "New Value", value="Updated text content"),
            ui.input_text(
                "new_placeholder", "New Placeholder", value="Updated placeholder text"
            ),
            ui.input_action_button("update", "Update Text Area", class_="btn-primary"),
            width=1 / 2,
        ),
    ),
    # Display current values for verification
    ui.card(ui.card_header("Current Values"), ui.output_text("show_values")),
    fillable_mobile=True,
)


def server(input, output, session):
    # Display current values
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


app = App(app_ui, server)
