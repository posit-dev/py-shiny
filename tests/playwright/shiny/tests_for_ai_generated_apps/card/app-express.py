from shiny.express import render, ui

# Set page options
ui.page_opts(fillable=True)

# Card with all possible parameters
with ui.card(
    id="demo_card",
    full_screen=True,  # Allow card to be expanded to full screen
    height="300px",  # Set card height
    fill=True,  # Allow card to grow/shrink to fit container
    class_="my-4",  # Add custom CSS classes
):
    # Card header
    ui.card_header("Card Demo", "This demonstrates all card parameters")

    # Card body content
    ui.markdown(
        """
    This is the main content of the card.
    The card has various parameters set including:

    * full_screen=True - allows expanding to full screen
    * height='300px' - sets fixed height
    * fill=True - allows card to grow/shrink
    * class_='my-4' - adds custom CSS classes
    """
    )

    # Card footer
    ui.card_footer("Card Footer", class_="text-muted")

# Another card showing dynamic content
with ui.card(id="dynamic_card", full_screen=True, height="200px", class_="mt-4"):
    ui.card_header("Dynamic Content Demo")

    @render.text
    def dynamic_content():
        return "This card shows how to include dynamic content using render functions"
