from shiny import App, reactive, render, ui
from shiny.ui import div, h3
from math import radians, sin, cos

# Import modules for plot rendering
import matplotlib.pyplot as plt

app_ui = ui.page_fluid(
    div(h3("Spirograph")),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_slider("start", "Start Angle", 0, 10, 2),
            ui.input_slider("step", "Step Angle", 10, 100, 10),
            ui.input_slider("origin", "Origin", min=0, max=50, value=(0, 0)),
        ),
        ui.panel_main(
            ui.output_plot("plot"),
        ),
    ),
)

def server(input, output, session):
    @reactive.Calc
    def calculate_points():
        points = []
        values = (input.origin()[0], input.origin()[1])
        points.append(values)
        points.append((cos(radians(input.start())), sin(radians(input.start()))))

        for i in range(input.start() + input.step(), 360 + input.step(), input.step()):
            x = cos(radians(i))
            y = sin(radians(i))
            points.append((x,y))
            points.append(values)
            points.append((x,y))

        x,y = zip(*points) # separate the tuples into x and y coordinates.

        return x,y


    @output
    @render.plot
    def plot():
        a, b = calculate_points()
        plt.plot(a, b) #plots the points, drawing lines between each point

app = App(app_ui, server, debug=True)
