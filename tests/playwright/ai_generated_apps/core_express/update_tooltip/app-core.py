from shiny import App, reactive, ui

# Define the UI
app_ui = ui.page_fillable(
    # Add Font Awesome for icons
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css",
        ),
    ),
    # Create a container card
    ui.card(
        ui.card_header("Tooltip Demo"),
        # Control buttons in a row
        ui.layout_column_wrap(
            ui.input_action_button(
                "btn_show",
                "Show tooltip",
                class_="btn btn-info",
                icon=ui.tags.i(class_="fa-solid fa-eye"),
            ),
            ui.input_action_button(
                "btn_close",
                "Close tooltip",
                class_="btn btn-warning",
                icon=ui.tags.i(class_="fa-solid fa-eye-slash"),
            ),
            ui.input_action_button(
                "btn_update",
                "Update tooltip",
                class_="btn btn-success",
                icon=ui.tags.i(class_="fa-solid fa-sync"),
            ),
            width=1 / 3,
        ),
        ui.hr(),
        # Center the tooltip button
        ui.div(
            ui.tooltip(
                ui.input_action_button(
                    "btn_w_tooltip",
                    "Hover over me!",
                    class_="btn btn-primary btn-lg",
                    icon=ui.tags.i(class_="fa-solid fa-info-circle"),
                ),
                "Initial tooltip message - try the buttons above!",
                id="tooltip_id",
                placement="right",
            ),
            class_="d-flex justify-content-center align-items-center",
            style="height: 200px;",
        ),
    ),
)


# Define the server
def server(input, output, session):
    # Effect to show tooltip
    @reactive.effect
    @reactive.event(input.btn_show)
    def _():
        ui.update_tooltip("tooltip_id", show=True)

    # Effect to close tooltip
    @reactive.effect
    @reactive.event(input.btn_close)
    def _():
        ui.update_tooltip("tooltip_id", show=False)

    # Effect to update tooltip content and show it
    @reactive.effect
    @reactive.event(input.btn_update)
    def _():
        # Create dynamic content based on number of clicks
        count = input.btn_update()
        content = f"Tooltip updated {count} time{'s' if count > 1 else ''}!"
        # Update tooltip with new content and show it
        ui.update_tooltip("tooltip_id", content, show=True)

    # Show notification when button with tooltip is clicked
    @reactive.effect
    @reactive.event(input.btn_w_tooltip)
    def _():
        ui.notification_show(
            "Button clicked!", duration=2, type="message", close_button=True
        )


# Create and return the app
app = App(app_ui, server)
