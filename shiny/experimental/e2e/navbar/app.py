from __future__ import annotations

import shiny.experimental as x
from shiny import App, ui
from shiny.types import NavSetArg

my_sidebar = x.ui.sidebar("My sidebar!!", open="open", title="Barret")


def nav_with_content(letter: str, prefix: str) -> ui._navs.Nav:
    return ui.nav(letter, ui.markdown(f"`{prefix}`: tab {letter} content"))


def nav_items(prefix: str) -> list[NavSetArg]:
    a = nav_with_content("a", prefix)
    b = nav_with_content("b", prefix)
    github = ui.nav_control(
        ui.tags.a(
            # ui.icon("github"),
            "Shiny",
            href="https://github.com/rstudio/shiny",
            target="_blank",
        ),
    )
    space = ui.nav_spacer()
    other = ui.nav_menu(
        "Other links",
        nav_with_content("c", prefix),
        ui.nav_control(
            ui.tags.a(
                # icon("r-project"),
                "RStudio",
                href="https://rstudio.com",
                target="_blank",
            ),
        ),
        align="right",
    )
    return [a, b, github, space, other]


app = App(
    ui=x.ui.page_navbar(
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
            ui.h4("navset_tab_card()"),
            x.ui.navset_tab_card(
                *nav_items("navset_tab_card()"),
                sidebar=my_sidebar,
            ),
            ui.h4("navset_pill_card()"),
            x.ui.navset_pill_card(
                *nav_items("navset_pill_card()"),
                sidebar=my_sidebar,
            ),
            # Do not include `navset_bar()` in example. Ok for testing only
            ui.h4("navset_bar()"),
            x.ui.navset_bar(
                *nav_items("navset_bar()"),
                title="Test!",
                sidebar=my_sidebar,
            ),
        ),
    ),
    server=None,
)
