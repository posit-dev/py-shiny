from shiny import App, Inputs, Outputs, Session, ui

# Define the UI
app_ui = ui.page_fluid(
    ui.include_css("./www/style.css"),  # Reference the external CSS file
    ui.include_js("./www/customjs.js"),
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
