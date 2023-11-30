import matplotlib.pyplot as plt
import numpy as np

from shiny import render, ui
from shiny.express import input, layout


with layout.accordion(id="express_accordion", open=["Panel 1", "Panel 2"]):
    with layout.accordion_panel("Panel 1"):
        ui.input_slider("a", "A", 1, 100, 50)

    with layout.accordion_panel("Panel 2"):

        @render.text
        def txt():
            return f"a = {input.a()}"


ui.tags.style(
    """
    #shell div{
    background-color: #00000022}
"""
)
with layout.div(id="shell"):
    with layout.row():
        with layout.column(width=8):
            with layout.row():
                "R1C1R1"
            with layout.row():
                with layout.row():
                    with layout.column(width=8):
                        with layout.row():
                            "R1C1R2-R1C1R1"
                        with layout.row():
                            "R1C1R2-R1C1R2"

                    with layout.column(width=4):
                        "R1C1R2-R1C2"

        with layout.column(width=4):
            "R1C2"

ui.input_file
with layout.column(width=6):
    # check height is below 300px - bounding box
    with layout.navset_card_tab(id="express_navset_card_tab"):
        with layout.nav(title="Two"):
            ...


with layout.column(width=6):
    with layout.row():
        with layout.navset_tab(id="express_navset_tab"):
            for fn_txt, fn in [
                ("pre", layout.pre),
                ("div", layout.div),
                ("span", layout.span),
            ]:
                with layout.nav(title=fn_txt):
                    for i in range(3):
                        with fn():
                            ui.HTML(f"{fn_txt} {i}")


@render.plot
def histogram():
    np.random.seed(19680801)
    x = 100 + 15 * np.random.randn(437)
    plt.hist(x, input.a(), density=True)
