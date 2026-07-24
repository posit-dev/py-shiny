from pathlib import Path

from shared import filler_text

from shiny.express import input, render, ui

ui.page_opts(
    title="Theme Example",
    theme=Path(__file__).parent / "css" / "shiny-theme-demo.css",
)

with ui.sidebar(title="Parameters"):
    ui.input_numeric("n", "N", min=0, max=100, value=20)

ui.h2("Output")


@render.code
def txt():
    return f"n*2 is {input.n() * 2}"


ui.markdown(filler_text)
