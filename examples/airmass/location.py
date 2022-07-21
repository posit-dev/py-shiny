from typing import Optional

import ipyleaflet as L
from shiny import Inputs, Outputs, Session, module, reactive, req, ui
from shinywidgets import output_widget, reactive_read, register_widget

# ============================================================
# Module: location
# ============================================================


@module.ui
def location_ui(
    label: str = "Location",
    *,
    lat: Optional[float],
    long: Optional[float],
) -> ui.TagChildArg:
    return ui.div(
        ui.input_numeric("lat", "Latitude", value=None),
        ui.input_numeric("long", "Longitude", value=None),
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
    marker = L.Marker(location=(52, 100))

    @reactive.Effect
    @reactive.isolate()
    def _():
        if not input.lat() and not input.long():
            ui.insert_ui(
                ui.tags.script(
                    """
                    navigator.geolocation.getCurrentPosition(
                        ({coords}) => {
                            const {latitude, longitude, altitude} = coords;
                            Shiny.setInputValue("#HERE#", {latitude, longitude});
                        },
                        (err) => {
                            Shiny.setInputValue("#HERE#", null);
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

    def move(lat: float, long: float) -> None:
        lat = round(lat, 8)
        long = round(long, 8)
        marker.location = (lat, long)
        if marker not in map.layers:
            map.add_layer(marker)
        ui.update_text("lat", value=lat)
        ui.update_text("long", value=long)

    def on_map_interaction(**kwargs):
        if kwargs.get("type") == "click":
            coords = kwargs.get("coordinates")
            move(coords[0], coords[1])

    map.on_interaction(on_map_interaction)

    def on_marker_move():
        move(marker.location[0], marker.location[1])

    marker.on_move(on_marker_move)

    register_widget("map", map)

    @reactive.Effect
    def detect_location():
        coords = input.here()
        if coords and not input.lat() and not input.long():
            ui.update_numeric("lat", value=coords["latitude"])
            ui.update_numeric("long", value=coords["longitude"])

    @reactive.Effect
    def sync_map_lat():
        req(input.lat() is not None)
        lat = float(input.lat())
        if marker.location[0] != lat:
            marker.location = (lat, marker.location[1])
        if marker not in map.layers:
            map.add_layer(marker)
        map.center = marker.location

    @reactive.Effect
    def sync_map_long():
        req(input.long() is not None)
        long = float(input.long())
        if marker.location[1] != long:
            marker.location = (marker.location[0], long)
        if marker not in map.layers:
            map.add_layer(marker)
        map.center = marker.location

    @reactive.Calc
    def location():
        req(input.lat() is not None, input.long() is not None)
        long = float(input.long())
        if wrap_long:
            long = (long + 180) % 360 - 180
        try:
            return (float(input.lat()), long)
        except ValueError:
            raise ValueError("Invalid latitude/longitude specification")

    return location
