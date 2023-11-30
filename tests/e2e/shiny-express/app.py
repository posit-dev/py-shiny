# "set_page",
# "sidebar",
# "page_sidebar",


import matplotlib.pyplot as plt
import numpy as np

from shiny import render, ui
from shiny.express import input, layout

# with layout.page_sidebar():
#     with layout.sidebar():
#         "sidebar-content"
#     "main-content"
# with layout.sidebar():
#     "sidebar-content"
with layout.accordion(id="express_accordion", open=["Panel 1", "Panel 2"]):
    with layout.accordion_panel("Panel 1"):
        ui.input_slider("a", "A", 1, 100, 50)

    with layout.accordion_panel("Panel 2"):

        @render.text
        def txt():
            return f"a = {input.a()}"

    # can't get this working
    # with layout.sidebar(id="sidebar"):


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
                ...
            with layout.row():
                with layout.row():
                    with layout.column(width=8):
                        with layout.row():
                            ...
                        with layout.row():
                            ...

                    with layout.column(width=4):
                        ...

        with layout.column(width=4):
            ...


with layout.page_sidebar():
    with layout.sidebar():
        "sidebar-content"
with layout.column(width=6):
    with layout.navset_card_tab(id="express_navset_card_tab"):
        with layout.nav(title="Two"):
            ui.input_action_button("btn", "Click here...")


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
            # with layout.nav(title="pre"):
            #     for i in range(4):
            #         with layout.pre(title="Four"):
            #             ui.HTML(i)
            # with layout.nav(title="div"):
            #     with layout.div():
            #         ui.input_slider("d", "D", 1, 100, 50)
            # with layout.nav(title="row"):
            #     with layout.row():
            #         ui.input_slider("f", "F", 1, 100, 50)
            # with layout.nav(title="span"):
            #     with layout.span():
            #         "text1"
            #     with layout.span():
            #         ui.HTML("text2")
            # with layout.nav(title="card"):
            #     with layout.card():
            #         ui.input_slider("j", "J", 1, 100, 50)

    with layout.page_fillable(title="Fillable Page"):
        ui.input_slider("e", "E", 1, 100, 50)

    with layout.page_fluid(title="Fluid Page"):
        ui.input_slider("h", "H", 1, 100, 50)


@render.plot
def histogram():
    np.random.seed(19680801)
    x = 100 + 15 * np.random.randn(437)
    plt.hist(x, input.a(), density=True)
