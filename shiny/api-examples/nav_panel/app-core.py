from typing import List

from shiny import App, Inputs, Outputs, Session, reactive, ui
from shiny.types import NavSetArg


def nav_controls(prefix: str) -> List[NavSetArg]:
    return [
        ui.nav_panel("a", prefix + ": tab a content"),
        ui.nav_panel("b", prefix + ": tab b content"),
        ui.nav_panel("c", prefix + ": tab c content"),
        ui.nav_spacer(),
        ui.nav_menu(
            "Links",
            ui.nav_control(
                ui.a(
                    "Shiny",
                    href="https://shiny.posit.co/py/",
                    target="_blank",
                )
            ),
            "----",
            "Plain text",
            "----",
            ui.nav_control(
                ui.a(
                    "Posit",
                    href="https://posit.co",
                    target="_blank",
                )
            ),
            align="right",
        ),
    ]


app_ui = ui.page_navbar(
    *nav_controls("page_navbar"),
    title="page_navbar()",
    id="navbar_id",
    footer=ui.div(
        {"style": "width:80%;margin: 0 auto"},
        ui.tags.style(
            """
            h4 {
                margin-top: 3em;
            }
            """
        ),
        ui.h4("navset_tab()"),
        ui.navset_tab(*nav_controls("navset_tab()")),
        ui.h4("navset_pill()"),
        ui.navset_pill(*nav_controls("navset_pill()")),
        ui.h4("navset_underline()"),
        ui.navset_underline(*nav_controls("navset_underline()")),
        ui.h4("navset_card_tab()"),
        ui.navset_card_tab(*nav_controls("navset_card_tab()")),
        ui.h4("navset_card_pill()"),
        ui.navset_card_pill(*nav_controls("navset_card_pill()")),
        ui.h4("navset_card_underline()"),
        ui.navset_card_underline(*nav_controls("navset_card_underline()")),
        ui.h4("navset_pill_list()"),
        ui.navset_pill_list(*nav_controls("navset_pill_list()")),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    def _():
        print("Current navbar page: ", input.navbar_id())


app = App(app_ui, server)
