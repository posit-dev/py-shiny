from icons import arrow_up, piggy_bank

from shiny import App, ui

app_ui = ui.page_fluid(
    ui.layout_column_wrap(
        ui.value_box(
            "KPI Title",
            ui.h1(ui.HTML("$1 <i>Billion</i> Dollars")),
            ui.span(arrow_up, " 30% VS PREVIOUS 30 DAYS"),
            showcase=piggy_bank,
            theme="bg-gradient-orange-cyan",
            full_screen=True,
        ),
        ui.value_box(
            "KPI Title",
            ui.h1(ui.HTML("$1 <i>Billion</i> Dollars")),
            ui.span(arrow_up, " 30% VS PREVIOUS 30 DAYS"),
            showcase=piggy_bank,
            theme="text-green",
            showcase_layout="top right",
            full_screen=True,
        ),
        ui.value_box(
            "KPI Title",
            ui.h1(ui.HTML("$1 <i>Billion</i> Dollars")),
            ui.span(arrow_up, " 30% VS PREVIOUS 30 DAYS"),
            showcase=piggy_bank,
            theme="purple",
            showcase_layout="bottom",
            full_screen=True,
        ),
    )
)


app = App(app_ui, server=None)
