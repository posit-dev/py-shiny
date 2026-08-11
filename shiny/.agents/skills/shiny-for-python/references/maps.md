# Geographic views in Shiny dashboards

## Overview

Use a map only when location, distance, or spatial pattern changes the decision. A
ranked bar chart is usually clearer for comparing named regions. When a map is useful,
choose the lightest library that supplies the needed interaction and can handle the
data volume.

## Contents

- Choose a map stack
- Prepare geographic data
- Render a Plotly point map
- Use widget-native maps safely
- Control overplotting and payload size
- Presentation and accessibility
- Common mistakes

## Choose a map stack

| Need | Good default | Tradeoff |
|---|---|---|
| Reactive point or density map with Plotly already installed | `plotly.express.scatter_map` / `density_map` through shinywidgets | Simple and cohesive with other Plotly charts; fewer specialized GIS controls |
| Leaflet layers and bidirectional widget events | `ipyleaflet` through `@render_widget` | Rich map interaction; adds ipywidgets/widget dependencies |
| Tens of thousands or more geometries | `lonboard` through `@render_widget` | GPU-accelerated; requires careful GeoArrow/geopandas data preparation |
| Static HTML map with plugins | Folium in a UI/HTML output | Easy marker clusters and plugins, but replacement HTML is less suitable for continuous two-way interaction |

Declare optional dependencies explicitly. Do not assume a package is installed because
another development or benchmark environment happened to include it.

## Prepare geographic data

Convert coordinates to numeric, drop invalid rows, and validate ranges before
rendering. Keep longitude on the x axis and latitude on the y axis.

```python
frame = filtered_locations().copy()
frame["latitude"] = pd.to_numeric(frame["latitude"], errors="coerce")
frame["longitude"] = pd.to_numeric(frame["longitude"], errors="coerce")
frame = frame.dropna(subset=["latitude", "longitude"])
frame = frame[
    frame["latitude"].between(-90, 90)
    & frame["longitude"].between(-180, 180)
]
```

Treat zero rows as a normal dashboard state. Show "No locations match these filters"
instead of calculating a `NaN` center or leaving a blank canvas.

## Render a Plotly point map

For a conventional point map, use the same shinywidgets pairing as other Plotly
charts. Recompute the center from the filtered frame and use a light basemap so marks
and labels remain legible.

```python
import plotly.express as px
from shinywidgets import output_widget, render_plotly

map_card = ui.card(
    ui.card_header("Customer locations"),
    output_widget("customer_map", height="520px"),
    full_screen=True,
)

@render_plotly
def customer_map():
    frame = clean_locations(filtered_customers())
    if frame.empty:
        return empty_map_figure("No customer locations match these filters")

    fig = px.scatter_map(
        frame,
        lat="latitude",
        lon="longitude",
        color="segment",
        color_discrete_map=SEGMENT_COLORS,
        hover_name="customer_name",
        hover_data={
            "city": True,
            "revenue": ":$,.0f",
            "latitude": False,
            "longitude": False,
        },
        zoom=4,
        center={
            "lat": float(frame["latitude"].mean()),
            "lon": float(frame["longitude"].mean()),
        },
    )
    fig.update_layout(
        map_style="carto-positron",
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        legend={"orientation": "h"},
    )
    return fig
```

Implement `empty_map_figure()` with an annotation-only
`plotly.graph_objects.Figure`; do not invent placeholder coordinates.

## Use widget-native maps safely

For ipyleaflet or lonboard, pair `output_widget("map_id")` with
`@render_widget`. Construct the map/widget inside the render function so each Shiny
session owns its widget. Module-scope data and imports are fine; module-scope widget
instances are not.

```python
from shinywidgets import output_widget, render_widget

@render_widget
def territory_map():
    from ipyleaflet import CircleMarker, Map, basemaps

    frame = clean_locations(filtered_territories())
    center = (39.5, -98.35) if frame.empty else (
        float(frame["latitude"].mean()),
        float(frame["longitude"].mean()),
    )
    widget = Map(center=center, zoom=4, basemap=basemaps.CartoDB.Positron)
    for row in frame.itertuples():
        widget.add(CircleMarker(location=(row.latitude, row.longitude), radius=6))
    return widget
```

The simple loop is appropriate only for a modest number of points. For many points,
send one GeoJSON/layer object, cluster or aggregate, or switch to lonboard. Use the
map library's documented event API when map clicks or bounds must update reactive
state; do not reach through undocumented renderer attributes to mutate a widget.

## Control overplotting and payload size

- Below a few thousand simple points, a normal point layer is often sufficient.
- When points overlap, cluster, aggregate to regions/hexagons, or use a density layer.
- When every point must remain interactive at larger scale, prefer a GPU-backed layer
  such as lonboard and trim tooltip columns.
- Keep category legends short and stable. Use size only with nonnegative, finite
  values and a clear legend.
- Recompute or fit the viewport after filters change; do not leave users looking at an
  unrelated hard-coded city.

## Presentation and accessibility

- Put the map in a titled, full-screen card with an explicit height of roughly
  420-560 px.
- Use a subdued light basemap unless the data requires another style.
- Provide a table or textual summary for users who cannot interpret or operate the
  map.
- Do not communicate status by marker color alone; add labels, shapes, or hover text.
- Escape or sanitize untrusted strings before placing them in HTML popups.

## Common mistakes

- Using a map when geography is incidental.
- Constructing one widget globally and sharing it across user sessions.
- Rendering thousands of individual marker objects in a Python loop.
- Forgetting invalid-coordinate and empty-filter handling.
- Depending on private methods or renderer internals for updates.
- Hard-coding the viewport so filtered points appear off-screen.
