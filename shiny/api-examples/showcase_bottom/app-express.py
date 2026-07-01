from icons import piggy_bank

from shiny.express import ui

with ui.layout_columns():
    with ui.value_box(
        showcase=piggy_bank,
        showcase_layout=ui.showcase_bottom(),
        theme="purple",
        full_screen=True,
    ):
        "KPI Title"
        "$1 Billion Dollars"
        "Up 30% VS PREVIOUS 30 DAYS"
