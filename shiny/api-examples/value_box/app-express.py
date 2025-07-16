from icons import piggy_bank

from shiny.express import ui

with ui.layout_columns():
    with ui.value_box(
        showcase=piggy_bank, theme="bg-gradient-orange-red", full_screen=True
    ):
        "KPI Title"
        "$1 Billion Dollars"
        "Up 30% VS PREVIOUS 30 DAYS"

    with ui.value_box(
        showcase=piggy_bank,
        theme="text-green",
        showcase_layout="top right",
        full_screen=True,
    ):
        "KPI Title"
        "$1 Billion Dollars"
        "Up 30% VS PREVIOUS 30 DAYS"

    with ui.value_box(
        showcase=piggy_bank, theme="purple", showcase_layout="bottom", full_screen=True
    ):
        "KPI Title"
        "$1 Billion Dollars"
        "Up 30% VS PREVIOUS 30 DAYS"
