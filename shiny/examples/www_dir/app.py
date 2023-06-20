from pathlib import Path

from shiny import App, Inputs, Outputs, Session, ui

app_ui = ui.page_fluid(
    ui.tags.link(href="css/styles.css", rel="stylesheet"),
    ui.tags.div(
        "If you see this text, it failed",
        id="target",
        style="background-color: red;",
    ),
    ui.tags.script(src="js/changetext.js"),
    ui.tags.div(
        "This box should be green: ",
        ui.tags.div(
            id="box",
            style="width: 100px; height:100px; border: 1px solid black;",
        ),
    ),
    "There should be a slider below: ",
    ui.input_slider("n", "N", min=1, max=100, value=50),
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app_dir = Path(__file__).parent.resolve()
app = App(app_ui, server, static_assets=str(app_dir / "www"))
