from shiny.express import ui

ui.tags.style(
    """
    #shell div{
    background-color: #00000022}
"""
)
with ui.div(id="shell"):
    with ui.layout_columns(col_widths=[8, 4]):
        "R1C1R1"
        with ui.layout_columns(col_widths=[8, 4]):
            with ui.div():
                ui.div("R1C1R2-R1C1R1")

                ui.div("R1C1R2-R1C1R2")

            "R1C1R2-R1C2"

        "R1C2"

with ui.layout_columns(col_widths=[6, 6]):
    # check height is below 300px - bounding box
    with ui.navset_card_tab(id="express_navset_card_tab"):
        with ui.nav_panel(title="Two"):
            ...

    with ui.navset_tab(id="express_navset_tab"):
        for fn_txt, fn in [
            ("pre", ui.pre),
            ("div", ui.div),
            ("span", ui.span),
        ]:
            with ui.nav_panel(title=fn_txt):
                for i in range(3):
                    with fn():
                        ui.HTML(f"{fn_txt} {i}")
