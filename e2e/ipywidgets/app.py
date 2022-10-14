from htmltools import css
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, reactive_read, register_widget

import ipyleaflet as L

app_ui = ui.page_fluid(
    ui.div(
        ui.input_slider("zoom", "Map zoom level", value=12, min=1, max=18),
        ui.output_ui("map_bounds"),
        style=css(
            display="flex", justify_content="center", align_items="center", gap="2rem"
        ),
    ),
    output_widget("map"),
)


def server(input, output, session):
    # Initialize and display when the session starts (1)
    map = L.Map(center=(51.476852, -0.000500), zoom=12, scroll_wheel_zoom=True)
    # Add a distance scale
    map.add_control(L.leaflet.ScaleControl(position="bottomleft"))
    register_widget("map", map)

    # When the slider changes, update the map's zoom attribute (2)
    @reactive.Effect
    def _():
        map.zoom = input.zoom()

    # When zooming directly on the map, update the slider's value (2 and 3)
    @reactive.Effect
    def _():
        ui.update_slider("zoom", value=reactive_read(map, "zoom"))

    # Everytime the map's bounds change, update the output message (3)
    @output
    @render.ui
    def map_bounds():
        center = reactive_read(map, "center")
        if len(center) == 0:
            return

        lat = round(center[0], 4)
        lon = (center[1] + 180) % 360 - 180
        lon = round(lon, 4)

        return ui.p(f"Latitude: {lat}", ui.br(), f"Longitude: {lon}")


app = App(app_ui, server)
