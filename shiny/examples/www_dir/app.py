from shiny import *

app_ui = ui.page_fluid(
    ui.tags.script(src="js/alert.js"),
    ui.tags.link(href="css/styles.css", rel="stylesheet"),
    "If you see this page before 'OK'-ing the alert box, something went wrong",
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)
