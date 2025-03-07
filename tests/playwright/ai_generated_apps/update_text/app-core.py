from shiny import App, reactive, render, ui

# Define the UI
app_ui = ui.page_fillable(
    # Layout with two columns
    ui.layout_column_wrap(
        # First card with text input
        ui.card(
            ui.card_header("Text Input Demo"),
            ui.input_text(
                "txt",
                "Original Text",
                value="Initial value",
                placeholder="Type something...",
            ),
            ui.output_text("current_value"),
        ),
        # Second card with control buttons
        ui.card(
            ui.card_header("Control Buttons"),
            ui.layout_column_wrap(
                ui.input_action_button(
                    "update_all", "Update All Parameters", class_="btn-primary mb-3"
                ),
                ui.input_action_button(
                    "update_label", "Update Label Only", class_="btn-secondary mb-3"
                ),
                ui.input_action_button(
                    "update_value", "Update Value Only", class_="btn-success mb-3"
                ),
                ui.input_action_button(
                    "update_placeholder",
                    "Update Placeholder Only",
                    class_="btn-info mb-3",
                ),
            ),
        ),
        width=1 / 2,
    ),
)


# Define the server
def server(input, output, session):
    # Render current value text
    @render.text
    def current_value():
        return f"Current value: {input.txt()}"

    # Effect for updating all parameters
    @reactive.effect
    @reactive.event(input.update_all)
    def _():
        ui.update_text(
            id="txt",
            label="Updated Label",
            value="Updated Value",
            placeholder="Updated Placeholder",
        )

    # Effect for updating label only
    @reactive.effect
    @reactive.event(input.update_label)
    def _():
        ui.update_text(id="txt", label=f"Label Updated {input.update_label()} times")

    # Effect for updating value only
    @reactive.effect
    @reactive.event(input.update_value)
    def _():
        ui.update_text(id="txt", value=f"Value Updated {input.update_value()} times")

    # Effect for updating placeholder only
    @reactive.effect
    @reactive.event(input.update_placeholder)
    def _():
        ui.update_text(
            id="txt",
            placeholder=f"Placeholder Updated {input.update_placeholder()} times",
        )


# Create and return the app
app = App(app_ui, server)
