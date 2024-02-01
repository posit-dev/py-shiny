import folium  # pyright: ignore[reportMissingTypeStubs]

from shiny import render
from shiny.express import input, ui

locations_coords = {
    "San Francisco": (37.79554, -122.39348),
    "Los Angeles": (34.05026, -118.25768),
    "New York": (40.71222, -74.00490),
}
ui.page_opts(full_width=False)

with ui.card(id="card"):
    "Static Map"
    folium.Map(  # pyright: ignore[reportUnknownMemberType,reportGeneralTypeIssues]
        location=locations_coords["San Francisco"], tiles="USGS.USTopo", zoom_start=12
    )
    ui.input_radio_buttons(
        "location", "Location", ["San Francisco", "New York", "Los Angeles"]
    )

    @render.express
    def folium_map():
        "Map inside of render express call"
        folium.Map(  # pyright: ignore[reportUnknownMemberType,reportGeneralTypeIssues]
            location=locations_coords[input.location()],
            tiles="cartodb positron",
            zoom_start=12,
        )
        input.location()
