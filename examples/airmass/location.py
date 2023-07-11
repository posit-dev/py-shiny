from typing import Optional

import ipyleaflet as L
from shinywidgets import output_widget, reactive_read, register_widget

from shiny import Inputs, Outputs, Session, module, reactive, req, ui

# ============================================================
# Module: location
# ============================================================


@module.ui
def location_ui(
    label: str = "Location",
    *,
    lat: Optional[float] = None,
    long: Optional[float] = None,
) -> ui.TagChild:
    return ui.div(
        ui.input_numeric("lat", "Latitude", value=lat),
        ui.input_numeric("long", "Longitude", value=long),
        ui.help_text("Click to select location"),
        output_widget("map", height="200px"),
        ui.tags.style(
            """
            .jupyter-widgets.leaflet-widgets {
                height: 100% !important;
            }
            """
        ),
    )


@module.server
def location_server(
    input: Inputs, output: Outputs, session: Session, *, wrap_long: bool = True
):
    map = L.Map(center=(0, 0), zoom=1, scoll_wheel_zoom=True)
    with reactive.isolate():
        marker = L.Marker(location=(input.lat() or 0, input.long() or 0))

    with reactive.isolate():  # Use this to ensure we only execute one time
        if input.lat() is None and input.long() is None:
            ui.notification_show(
                "Searching for location...", duration=99999, id="searching"
            )
            ui.insert_ui(
                ui.tags.script(
                    """
                    navigator.geolocation.getCurrentPosition(
                        ({coords}) => {
                            const {latitude, longitude, altitude} = coords;
                            Shiny.setInputValue("#HERE#", {latitude, longitude});
                        },
                        (err) => {
                            Shiny.setInputValue("#HERE#", {latitude: 0, longitude: 0});
                        },
                        {maximumAge: Infinity, timeout: Infinity}
                    )
                    """.replace(
                        "#HERE#", module.resolve_id("here")
                    )
                ),
                selector="body",
                where="beforeEnd",
                immediate=True,
            )

    @reactive.isolate()
    def update_text_inputs(lat: Optional[float], long: Optional[float]) -> None:
        req(lat is not None, long is not None)
        lat = round(lat, 8)
        long = round(long, 8)
        if lat != input.lat():
            input.lat.freeze()
            ui.update_text("lat", value=lat)
        if long != input.long():
            input.long.freeze()
            ui.update_text("long", value=long)
        map.center = (lat, long)

    @reactive.isolate()
    def update_marker(lat: Optional[float], long: Optional[float]) -> None:
        req(lat is not None, long is not None)
        lat = round(lat, 8)
        long = round(long, 8)
        if marker.location != (lat, long):
            marker.location = (lat, long)
        if marker not in map.layers:
            map.add_layer(marker)
        map.center = marker.location

    def on_map_interaction(**kwargs):
        if kwargs.get("type") == "click":
            lat, long = kwargs.get("coordinates")
            update_text_inputs(lat, long)

    map.on_interaction(on_map_interaction)

    register_widget("map", map)

    @reactive.Effect
    def _():
        coords = reactive_read(marker, "location")
        if coords:
            update_text_inputs(coords[0], coords[1])

    @reactive.Effect
    def sync_autolocate():
        coords = input.here()
        ui.notification_remove("searching")
        if coords and not input.lat() and not input.long():
            update_text_inputs(coords["latitude"], coords["longitude"])

    @reactive.Effect
    def sync_inputs_to_marker():
        update_marker(input.lat(), input.long())

    @reactive.Calc
    def location():
        """Returns tuple of (lat,long) floats--or throws silent error if no lat/long is
        selected"""

        # Require lat/long to be populated before we can proceed
        req(input.lat() is not None, input.long() is not None)

        try:
            long = input.long()
            # Wrap longitudes so they're within [-180, 180]
            if wrap_long:
                long = (long + 180) % 360 - 180
            return (input.lat(), long)
        except ValueError:
            raise ValueError("Invalid latitude/longitude specification")

    return location
