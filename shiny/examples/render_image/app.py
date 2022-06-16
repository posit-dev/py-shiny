from shiny import *
from shiny.types import ImgData

app_ui = ui.page_fluid(ui.output_image("image"))


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.image
    def image():
        from pathlib import Path

        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "rstudio-logo.png"), "width": "150px"}
        return img


app = App(app_ui, server)
