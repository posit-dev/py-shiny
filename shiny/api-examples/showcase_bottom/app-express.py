from icons import piggy_bank

from shiny.express import ui
from shiny.ui import showcase_bottom

with ui.value_box(
    showcase=piggy_bank,
    showcase_layout=showcase_bottom(),
    theme="purple",
    full_screen=True,
):
    "KPI Title"
    "$1 Billion Dollars"
    "Up 30% VS PREVIOUS 30 DAYS"
