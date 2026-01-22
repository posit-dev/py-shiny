from shiny import App, render, ui

# Define the UI
app_ui = ui.page_fluid(
    # Add Font Awesome CSS in the head section
    ui.tags.head(
        ui.HTML(
            '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">'
        )
    ),
    # Create accordion with panels
    ui.accordion(
        # Basic panel
        ui.accordion_panel(
            "Panel A", "This is a basic accordion panel with default settings."
        ),
        # Panel with custom icon
        ui.accordion_panel(
            "Panel B",
            "This panel has a custom star icon and is open by default.",
            icon=ui.HTML('<i class="fa-solid fa-star" style="color: gold;"></i>'),
        ),
        # Basic panel that starts closed
        ui.accordion_panel(
            "Panel C", "This is another basic panel that starts closed."
        ),
        # Panel with longer content
        ui.accordion_panel(
            "Panel D",
            ui.markdown(
                """
                This panel contains longer content to demonstrate scrolling:

                - Item 1
                - Item 2
                - Item 3

                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua.
                """
            ),
        ),
        id="acc_demo",
        open=["Panel B", "Panel D"],
        multiple=True,
    ),
    # Output for showing which panels are open
    ui.output_text("selected_panels"),
)


# Define the server
def server(input, output, session):
    @render.text
    def selected_panels():
        return f"Currently open panels: {input.acc_demo()}"


# Create and return the app
app = App(app_ui, server)
