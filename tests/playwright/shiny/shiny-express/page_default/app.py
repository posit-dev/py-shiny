from shiny import ui
from shiny.express import layout

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
