from shiny import *
from shiny.types import ImgData

app_ui = ui.page_fluid(ui.output_image("image"))


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.image
    def image():
        from pathlib import Path

        ex_dir = Path(__file__).resolve().parent.parent
        img: ImgData = {
            "src": str(ex_dir / "output_image" / "rstudio-logo.png"),
            "width": "150px",
        }
        return img


app = App(app_ui, server)
