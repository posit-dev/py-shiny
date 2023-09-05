from typing import List

from shiny import App, Inputs, Outputs, Session, reactive, ui
from shiny.types import NavSetArg


def nav_controls(prefix: str) -> List[NavSetArg]:
    return [
        ui.nav("A", prefix + ": tab a content", value="a"),
        ui.nav("b", prefix + ": tab b content", value="b"),
        ui.nav_control(
            ui.a(
                "Shiny",
                href="https://github.com/rstudio/shiny",
                target="_blank",
            )
        ),
        ui.nav_spacer(),
        ui.nav_menu(
            "Other links",
            ui.nav("C", prefix + ": tab c content", value="c"),
            "----",
            "Plain text",
            "----",
            ui.nav_control(
                ui.a(
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
        ui.tags.style(
            """
            h4 {
                margin-top: 3em;
            }
            """
        ),
        ui.h4("navset_tab()"),
        ui.navset_tab(*nav_controls("navset_tab()"), id="navset_tab"),
        ui.h4("navset_pill()"),
        ui.navset_pill(*nav_controls("navset_pill()"), id="navset_pill"),
        ui.h4("navset_card_tab()"),
        ui.navset_card_tab(*nav_controls("navset_card_tab()"), id="navset_card_tab"),
        ui.h4("navset_card_pill()"),
        ui.navset_card_pill(*nav_controls("navset_card_pill()"), id="navset_card_pill"),
        ui.h4("navset_pill_list()"),
        ui.navset_pill_list(*nav_controls("navset_pill_list()"), id="navset_pill_list"),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    def _():
        print("Current navbar page: ", input.navbar_id())


app = App(app_ui, server)
