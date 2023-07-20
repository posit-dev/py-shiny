from shiny import App, Inputs, Outputs, Session, render, ui
from shiny.types import ImgData

app_ui = ui.page_fluid(ui.output_image("image"))


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.image
    def image():
        from pathlib import Path

        ex_dir = Path(__file__).resolve().parent.parent
        img: ImgData = {
            "src": str(ex_dir / "output_image" / "posit-logo.png"),
            "width": "100px",
        }
        return img


app = App(app_ui, server)
