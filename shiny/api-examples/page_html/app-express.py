from pathlib import Path

from shiny.express import render, ui

ui.page_opts(html=Path(__file__).parent / "index.html")


@render.text
def greeting():
    return "Hello from the server!"
