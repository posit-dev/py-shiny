# app.py
from shiny import App, render, ui

# Define the main app UI
app_ui = ui.page_fluid(
    ui.h1("Shiny App with Tabs"),
    ui.navset_tab(
        ui.nav_panel(
            "Tab 1: Input & Output",  # Tab title
            ui.h3("Input and Text Output"),
            ui.input_text(
                "text_input", "Enter some text:", "Hello Shiny!"
            ),  # Text input component
            ui.output_text("output_text"),
        ),
        ui.nav_panel(
            "Tab 2: Slider & Plot",  # Tab title
            ui.h3("Slider and Plot Output"),
            ui.input_slider(
                "n_points", "Number of points:", min=10, max=100, value=50
            ),  # Slider input component
            ui.output_plot("output_plot"),
        ),
        ui.nav_panel(
            "Tab 3: Button & Message",  # Tab title
            ui.h3("Action Button and Message Output"),
            ui.input_action_button(
                "action_button", "Click me!"
            ),  # Action button component
            ui.output_text("output_message"),
        ),
        id="navset_Tab",
    ),
)


# Define the main app server function
def server(input, output, session):

    @render.text  # Decorator for verbatim text output
    def output_text():
        return f"You entered: {input.text_input()}"  # Accessing the text input value

    @render.plot  # Decorator for rendering plots
    def output_plot():
        import matplotlib.pyplot as plt
        import numpy as np

        # Generate some data based on the slider input
        x = np.linspace(0, 10, input.n_points())
        y = np.sin(x)

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_title("Dynamic Sine Wave")
        return fig

    @render.text  # Decorator for rendering simple text
    def output_message():
        # Respond when the action button is clicked
        if input.action_button() > 0:
            return "Button clicked!"
        return "Click the button."


# Create the Shiny app instance
app = App(app_ui, server)
