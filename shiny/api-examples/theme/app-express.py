from pathlib import Path

from shiny.express import input, render, ui

ui.page_opts(
    title="Theme Example",
    theme=Path(__file__).parent / "css" / "bootswatch-minty.min.css",
)

with ui.sidebar(title="Parameters"):
    ui.input_numeric("n", "N", min=0, max=100, value=20)

ui.h2("Output")


@render.code
def txt():
    return f"n*2 is {input.n() * 2}"


ui.markdown(
    """
**AI-generated filler text.** In the world of exotic fruits, the durian stands out with its spiky exterior and strong odor. Despite its divisive smell, many people are drawn to its rich, creamy texture and unique flavor profile. This tropical fruit is often referred to as the "king of fruits" in various Southeast Asian countries.

Durians are known for their large size and thorn-covered husk, which requires careful handling. The flesh inside can vary in color from pale yellow to deep orange, with a custard-like consistency that melts in your mouth. Some describe its taste as a mix of sweet, savory, and creamy, while others find it overpowering and pungent.
"""
)
