from pathlib import Path
from shiny import *

app_ui = ui.page_fluid(
    ui.tags.script(src="js/alert.js"),
    ui.tags.link(href="css/styles.css", rel="stylesheet"),
    "If you see this page before 'OK'-ing the alert box, something went wrong",
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app_dir = Path(__file__).parent.resolve()
app = App(app_ui, server, static_assets=str(app_dir / "www"))
