from pathlib import Path

from shiny import App, Inputs, Outputs, Session, ui

js_file = Path(__file__).parent / "js" / "customjs.js"
# We don't know what the temp dir will be called until we make it and that's what we need to reference
# in the app (ex. we can't just reference where it is pre-copy)
js2_file = (
    ui.include_js(js_file, method="link_files").attrs["src"][:-11] + "customjs2.js"
)
css_file = Path(__file__).parent / "css" / "style.css"

# Define the UI
app_ui = ui.page_fluid(
    ui.include_css(css_file, method="link_files"),
    ui.include_js(js_file, method="link_files"),
    ui.tags.script(src=str(js2_file)),
    ui.h1("Simple Shiny App with External CSS"),
    ui.div(
        ui.p("This is a simple Shiny app that demonstrates ui.include_css()"),
        ui.p("The styling comes from an external CSS file!"),
        class_="content",
    ),
)


# Define the server
def server(input: Inputs, output: Outputs, session: Session):
    pass


# Create and run the app
app = App(app_ui, server)
