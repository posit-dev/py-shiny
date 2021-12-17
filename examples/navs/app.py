# This will load the shiny module dynamically, without having to install it.
# This makes the debug/run cycle quicker.
import os
import sys

shiny_module_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, shiny_module_dir)


from shiny import *
from fontawesome import icon_svg

navs = navs_tab_card(
    # TODO: fix default selected
    nav_menu(
        "Menu",
        nav("Good", "good content"),
        nav("Bad", "bad"),
    ),
    nav("Ok", "ok"),
)

ui = page_fluid(navs)


def server(s: ShinySession):
    pass


app = ShinyApp(ui, server)
if __name__ == "__main__":
    app.run()
