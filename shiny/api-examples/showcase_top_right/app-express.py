from icons import piggy_bank

from shiny.express import ui
from shiny.ui import showcase_top_right

with ui.value_box(
    showcase=piggy_bank,
    showcase_layout=showcase_top_right(),
    theme="text-green",
    full_screen=True,
):
    "KPI Title"
    "$1 Billion Dollars"
    "Up 30% VS PREVIOUS 30 DAYS"
