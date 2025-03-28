from shiny import App, render, ui

# Define the UI
app_ui = ui.page_fillable(
    # Add Font Awesome CSS in the head section
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
        )
    ),
    # Card containing accordion
    ui.card(
        ui.accordion(
            # Basic Panel
            ui.accordion_panel(
                "Basic Panel",
                ui.markdown("This is a basic panel with just a title parameter"),
            ),
            # Panel with title and value
            ui.accordion_panel(
                "Panel with Value",
                ui.markdown("This panel has both a title and a value parameter"),
                value="panel2",
            ),
            # Panel with title, value, and icon
            ui.accordion_panel(
                "Panel with Icon",
                ui.markdown("This panel includes an icon parameter using Font Awesome"),
                value="panel3",
                icon=ui.tags.i(
                    class_="fa-solid fa-shield-halved", style="font-size: 1rem;"
                ),
            ),
            # Panel with title, value, icon, and custom attributes
            ui.accordion_panel(
                "Panel with Custom Attributes",
                ui.markdown(
                    "This panel demonstrates custom attributes (class and style)"
                ),
                value="panel4",
                icon=ui.tags.i(class_="fa-solid fa-star", style="font-size: 1rem;"),
                class_="custom-panel",
                style="background-color: #f8f9fa;",
            ),
            id="acc",
            open=True,
            multiple=True,
        ),
    ),
    # Output for selected panel
    ui.output_text("selected_panel"),
)


# Define the server
def server(input, output, session):
    @output
    @render.text
    def selected_panel():
        return f"Currently selected panel: {input.acc()}"


# Create the app
app = App(app_ui, server)
