import folium  # pyright: ignore[reportMissingTypeStubs]

from shiny import render, ui
from shiny.express import input, layout

locations_coords = {
    "San Francisco": (37.79554, -122.39348),
    "Los Angeles": (34.05026, -118.25768),
    "New York": (40.71222, -74.00490),
}
layout.set_page(layout.page_fixed())

with layout.card(id="card"):
    "Static Map"
    folium.Map(
        location=locations_coords["San Francisco"], tiles="USGS.USTopo", zoom_start=12
    )
    ui.input_radio_buttons(
        "location", "Location", ["San Francisco", "New York", "Los Angeles"]
    )

    @render.display
    def folium_map():
        "Map inside of render display call"
        folium.Map(
            location=locations_coords[input.location()],
            tiles="cartodb positron",
            zoom_start=12,
        )
        input.location()
