from shiny import App, render, ui

# Create sample choices with HTML content
choices = {
    "choice1": ui.span("Choice 1", style="color: red;"),
    "choice2": ui.span("Choice 2", style="color: blue;"),
    "choice3": ui.span("Choice 3", style="color: green;"),
}

# Define the UI
app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("Radio Buttons Example"),
        # Create radio buttons with all possible parameters
        ui.input_radio_buttons(
            id="radio_demo",  # Required: unique identifier
            label="Demo Radio Group",  # Required: label text
            choices=choices,  # Required: choices as dict with HTML content
            selected="choice1",  # Optional: initial selected value
            inline=True,  # Optional: display buttons inline
            width="300px",  # Optional: CSS width
        ),
        # Add some spacing
        ui.br(),
        # Output for displaying selection
        ui.output_text("selection"),
    )
)


# Define the server
def server(input, output, session):
    @output
    @render.text
    def selection():
        return f"You selected: {input.radio_demo()}"


# Create and return the app
app = App(app_ui, server)
