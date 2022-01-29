# To run this app:
#   python3 app.py

# Then point web browser to:
#   http://localhost:8000/

# Add parent directory to path, so we can find the prism module.
# (This is just a temporary fix)
import os
import sys

# This will load the shiny module dynamically, without having to install it.
# This makes the debug/run cycle quicker.
shiny_module_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, shiny_module_dir)

from shiny import *

ui = page_fluid(
    layout_sidebar(
        panel_sidebar(
            input_slider("n", "N", 0, 100, 20),
        ),
        panel_main(
            output_text_verbatim("txt", placeholder=True),
            output_plot("plot"),
        ),
    ),
)

# from htmltools.core import HTMLDocument
# from shiny import html_dependencies
# HTMLDocument(TagList(ui, html_dependencies.shiny_deps())).save_html("temp/app.html")


# A ReactiveVal which is exists outside of the session.
shared_val = ReactiveVal(None)


def server(session: Session):
    @reactive()
    def r():
        if session.input["n"] is None:
            return
        return session.input["n"] * 2

    @session.output("txt")
    async def _():
        val = r()
        return f"n*2 is {val}, session id is {get_current_session().id}"


app = ShinyApp(ui, server)

if __name__ == "__main__":
    app.run()
    # Alternately, to listen on a TCP port:
    # app.run(conn_type = "tcp")
