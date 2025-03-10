from shiny import App, render, ui

# Define the UI
app_ui = ui.page_fillable(
    # Card with all possible parameters
    ui.card(
        ui.card_header("Card Demo", "This demonstrates all card parameters"),
        ui.markdown(
            """
            This is the main content of the card.
            The card has various parameters set including:

            * full_screen=True - allows expanding to full screen
            * height='300px' - sets fixed height
            * fill=True - allows card to grow/shrink
            * class_='my-4' - adds custom CSS classes
            """
        ),
        ui.card_footer("Card Footer", class_="text-muted"),
        id="demo_card",
        full_screen=True,  # Allow card to be expanded to full screen
        height="300px",  # Set card height
        fill=True,  # Allow card to grow/shrink to fit container
        class_="my-4",  # Add custom CSS classes
    ),
    # Another card showing dynamic content
    ui.card(
        ui.card_header("Dynamic Content Demo"),
        ui.output_text("dynamic_content"),
        id="dynamic_card",
        full_screen=True,
        height="200px",
        class_="mt-4",
    ),
)


# Define the server
def server(input, output, session):
    @render.text
    def dynamic_content():
        return "This card shows how to include dynamic content using render functions"


# Create the app
app = App(app_ui, server)
