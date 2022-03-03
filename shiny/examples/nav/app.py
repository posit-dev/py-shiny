from typing import List

from shiny import *
from htmltools import JSXTag, h4
from fontawesome import icon_svg as icon


def nav_items(prefix: str) -> List[JSXTag]:
    return [
        ui.nav("a", prefix + ": tab a content"),
        ui.nav("b", prefix + ": tab b content"),
        ui.nav_item(
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
            ui.nav_item(
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
    *nav_items("page_navbar"),
    title="page_navbar()",
    bg="salmon",
    footer=ui.div(
        {"style": "width:80%;margin: 0 auto"},
        ui.h4("navs_tab()"),
        ui.navs_tab(*nav_items("navs_tab()")),
        h4("navs_pill()"),
        ui.navs_pill(*nav_items("navs_pill()")),
        h4("navs_tab_card()"),
        ui.navs_tab_card(*nav_items("navs_tab_card()")),
        h4("navs_pill_card()"),
        ui.navs_pill_card(*nav_items("navs_pill_card()")),
        h4("navs_pill_list()"),
        ui.navs_pill_list(*nav_items("navs_pill_list()")),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)
