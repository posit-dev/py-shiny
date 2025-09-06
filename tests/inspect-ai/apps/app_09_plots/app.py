# app.py
import matplotlib.pyplot as plt
import numpy as np

from shiny import App, module, render, ui


# Define the module UI function
@module.ui
def plot_module_ui():
    """Defines a module with two plots and inputs to control them."""
    return ui.div(
        ui.h3("Plot Module"),
        ui.input_slider(
            "n_points", "Number of points:", min=10, max=100, value=50
        ),  # Slider for points
        ui.row(  # Use ui.row to arrange plots side-by-side
            ui.column(6, ui.output_plot("plot1")),  # First plot in a column
            ui.column(6, ui.output_plot("plot2")),  # Second plot in a column
        ),
    )


# Define the module server function
@module.server
def plot_module_server(input, output, session):
    """Defines the server logic for the plot module."""

    @output
    @render.plot  # Decorator for rendering plots
    def plot1():
        # Generate some data for the first plot
        x = np.random.rand(input.n_points())
        y = np.random.rand(input.n_points())

        fig, ax = plt.subplots()
        ax.scatter(x, y)
        ax.set_title("Random Scatter Plot")
        return fig

    @output
    @render.plot  # Decorator for rendering plots
    def plot2():
        # Generate some data for the second plot
        x = np.linspace(0, 10, input.n_points())
        y = np.sin(x)

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_title("Sine Wave Plot")
        return fig


# Define the main app UI
app_ui = ui.page_fluid(
    ui.h1("Main Application with Plot Module"),
    plot_module_ui("my_plot_module"),  # Instantiate the module UI
)


# Define the main app server function
def server(input, output, session):
    plot_module_server("my_plot_module")  # Instantiate the module server


# Create the Shiny app instance
app = App(app_ui, server)
