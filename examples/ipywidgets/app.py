# This will load the shiny module dynamically, without having to install it.
# This makes the debug/run cycle quicker.
import os
import sys

shiny_module_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, shiny_module_dir)


from shiny import *

from ipywidgets import IntSlider

slider = IntSlider(value=40)

ui = page_fluid(
    # input_ipywidget("IntSlider", slider),
    output_ipywidget("ipyleaflet"),
    output_ui("widget_state"),
)


def server(ss: ShinySession):
    @ss.output("ipyleaflet")
    @render.ipywidget()
    def _():
        from ipyleaflet import Map, Marker, basemaps, basemap_to_tiles

        m = Map(
            basemap=basemap_to_tiles(
                basemaps.NASAGIBS.ModisTerraTrueColorCR, "2017-04-08"
            ),
            center=(52.204793, 360.121558),
            zoom=4,
        )

        m.add_layer(Marker(location=(52.204793, 360.121558)))

        return m

    @ss.output("widget_state")
    @render.ui()
    def _():
        try:
            return tags.pre(HTML(ss.input.ipyleaflet))
        except:
            return tags.pre(HTML("No input"))


app = ShinyApp(ui, server)
if __name__ == "__main__":
    app.run()
