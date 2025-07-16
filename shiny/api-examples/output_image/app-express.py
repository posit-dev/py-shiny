from shiny.express import render


@render.image
def image():
    from pathlib import Path

    dir = Path(__file__).resolve().parent
    img = {"src": str(dir / "posit-logo.png"), "width": "100px"}
    return img
