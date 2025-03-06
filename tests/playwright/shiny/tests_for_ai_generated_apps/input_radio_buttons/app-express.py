from shiny.express import input, render, ui

# Set page title
ui.page_opts(full_width=True)

# Create sample choices with HTML content
choices = {
    "choice1": ui.span("Choice 1", style="color: red;"),
    "choice2": ui.span("Choice 2", style="color: blue;"),
    "choice3": ui.span("Choice 3", style="color: green;"),
}

# Create a card to contain the radio buttons and output
with ui.card():
    ui.card_header("Radio Buttons Example")

    # Create radio buttons with all possible parameters
    ui.input_radio_buttons(
        id="radio_demo",  # Required: unique identifier
        label="Demo Radio Group",  # Required: label text
        choices=choices,  # Required: choices as dict with HTML content
        selected="choice1",  # Optional: initial selected value
        inline=True,  # Optional: display buttons inline
        width="300px",  # Optional: CSS width
    )

    # Add some spacing
    ui.br()

    # Display the current selection
    @render.text
    def selection():
        return f"You selected: {input.radio_demo()}"
