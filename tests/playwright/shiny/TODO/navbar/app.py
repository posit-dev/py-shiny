from __future__ import annotations

from shiny import App, ui
from shiny.types import NavSetArg

my_sidebar = ui.sidebar("Sidebar content", open="open", title="Sidebar title")


def nav_with_content(letter: str, prefix: str) -> ui._navs.NavPanel:
    return ui.nav_panel(letter, ui.markdown(f"`{prefix}`: tab {letter} content"))


def nav_items(prefix: str) -> list[NavSetArg]:
    a = nav_with_content("a", prefix)
    b = nav_with_content("b", prefix)
    c = nav_with_content("c", prefix)
    space = ui.nav_spacer()
    links = ui.nav_menu(
        "Links",
        ui.nav_control(
            ui.tags.a(
                # ui.icon("github"),
                "Shiny",
                href="https://github.com/posit-dev/py-shiny",
                target="_blank",
            ),
        ),
        "---",
        "Plain text",
        "---",
        ui.nav_control(
            ui.a(
                "Posit",
                href="https://posit.co",
                target="_blank",
            )
        ),
        align="right",
    )
    return [a, b, c, space, links]


app = App(
    ui=ui.page_navbar(
        # theme = bs_theme(),
        *nav_items("page_navbar()"),
        sidebar=my_sidebar,
        title="page_navbar()",
        bg="#0062cc",
        header=ui.markdown(
            "Testing app for `bslib::nav_spacer()` and `bslib::nav_item()` [#319](https://github.com/rstudio/bslib/pull/319)."
        ),
        footer=ui.div(
            {"style": "width:80%; margin: 0 auto"},
            ui.h4("navset_card_tab()"),
            ui.navset_card_tab(
                *nav_items("navset_card_tab()"),
                sidebar=my_sidebar,
            ),
            ui.h4("navset_card_pill()"),
            ui.navset_card_pill(
                *nav_items("navset_card_pill()"),
                sidebar=my_sidebar,
            ),
            # Do not include `navset_bar()` in example. Ok for testing only
            ui.h4("navset_bar()"),
            ui.navset_bar(
                *nav_items("navset_bar()"),
                title="Test!",
                sidebar=my_sidebar,
            ),
        ),
    ),
    server=None,
)
