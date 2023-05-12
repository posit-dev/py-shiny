import shiny.experimental as x
from shiny import App, ui
from shiny.types import NavSetArg


def nav_with_content(letter: str, prefix: str) -> ui._navs.Nav:
    return ui.nav(letter, ui.markdown(f"`{prefix}`: tab {letter} content"))


def nav_items(prefix: str) -> list[NavSetArg]:
    a = nav_with_content("a", prefix)
    b = nav_with_content("b", prefix)
    github = ui.nav_control(
        ui.tags.a(
            # ui.icon("github"),
            # ui.HTML(
            #     '<i class="fab fa-github" role="presentation" aria-label="github icon"></i>'
            # ),
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
        title="page_navbar()",
        bg="#0062cc",
        header=ui.markdown(
            "Testing app for `bslib::nav_spacer()` and `bslib::nav_item()` [#319](https://github.com/rstudio/bslib/pull/319)."
        ),
        footer=ui.div(
            {"style": "width:80%; margin: 0 auto"},
            ui.h4("navs_tab()"),
            ui.navset_tab(*nav_items("navs_tab()")),
            ui.h4("navs_pill()"),
            ui.navset_pill(*nav_items("navs_pill()")),
            ui.h4("navs_tab_card()"),
            ui.navset_tab_card(*nav_items("navs_tab_card()")),
            ui.h4("navs_pill_card()"),
            ui.navset_pill_card(*nav_items("navs_pill_card()")),
            ui.h4("navs_pill_list()"),
            ui.navset_pill_list(*nav_items("navs_pill_list()")),
            # Make sure body height does not change when taking screenshots
            ui.tags.style("body { min-height: 100vh; }"),
        ),
    ),
    server=None,
)
