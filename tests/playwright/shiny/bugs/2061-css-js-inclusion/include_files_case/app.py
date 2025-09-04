from pathlib import Path

from shiny import App, Inputs, Outputs, Session, ui

custom_css = ui.include_css(
    Path(__file__).parent / "css" / "style.css",
    method="link_files",
)

custom_js = ui.include_js(
    Path(__file__).parent / "js" / "customjs.js",
    method="link_files",
)

# path where the JS file's parent directory is mounted
href = custom_js.get_dependencies()[0].source_path_map()["href"]

# Define the UI
app_ui = ui.page_fluid(
    custom_css,
    custom_js,
    ui.tags.script(src=href + "/customjs2.js"),
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
