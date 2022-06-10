from typing import List

from shiny import *
from shiny.types import NavSetArg
from shiny.ui import h4
from fontawesome import icon_svg as icon


def nav_controls(prefix: str) -> List[NavSetArg]:
    return [
        ui.nav("a", prefix + ": tab a content"),
        ui.nav("b", prefix + ": tab b content"),
        ui.nav_control(
            ui.a(
                icon("github"),
                "Shiny",
                href="https://github.com/rstudio/shiny",
                target="_blank",
            )
        ),
        ui.nav_spacer(),
        ui.nav_menu(
            "Other links",
            ui.nav("c", prefix + ": tab c content"),
            "----",
            "Plain text",
            "----",
            ui.nav_control(
                ui.a(
                    icon("r-project"),
                    "RStudio",
                    href="https://rstudio.com",
                    target="_blank",
                )
            ),
            align="right",
        ),
    ]


app_ui = ui.page_navbar(
    *nav_controls("page_navbar"),
    title="page_navbar()",
    bg="#0062cc",
    inverse=True,
    id="navbar_id",
    footer=ui.div(
        {"style": "width:80%;margin: 0 auto"},
        h4("navset_tab()"),
        ui.navset_tab(*nav_controls("navset_tab()")),
        h4("navset_pill()"),
        ui.navset_pill(*nav_controls("navset_pill()")),
        h4("navset_tab_card()"),
        ui.navset_tab_card(*nav_controls("navset_tab_card()")),
        h4("navset_pill_card()"),
        ui.navset_pill_card(*nav_controls("navset_pill_card()")),
        h4("navset_pill_list()"),
        ui.navset_pill_list(*nav_controls("navset_pill_list()")),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect()
    def _():
        print("Current navbar page: ", input.navbar_id())


app = App(app_ui, server)
