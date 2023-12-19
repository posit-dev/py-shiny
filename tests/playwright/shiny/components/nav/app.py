from __future__ import annotations

from typing import Any, Callable, List

from htmltools import Tag

from shiny import App, ui
from shiny.types import NavSetArg
from shiny.ui import Sidebar

# TODO-karan; Make test that uses sidebar / no sidebar (where possible)
# TODO-karan; Make test that has/does not have a header & footer (where possible)
# TODO-karan; Test for title value (where possible)
# TODO-karan; Make test that has placement = "above" / "below" (where possible); Test in combination of with/without sidebar


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


def nav_headerfooter(prefix: str) -> tuple[Tag, Tag]:
    return (
        ui.span(f"{prefix}: Header"),
        ui.span(f"{prefix}: Footer"),
    )


def nav_title(prefix: str) -> Tag:
    return ui.span(f"{prefix}: Title")


def nav_sidebar(prefix: str) -> Sidebar:
    return ui.sidebar(
        f"{prefix}: Sidebar contents",
        title=f"{prefix}: Sidebar Title",
    )


def make_navset(
    name: str,
    fn: Callable[..., Any],
    *,
    controls: bool = True,
    title: bool = False,
    sidebar: bool = False,
    headerfooter: bool = False,
):
    prefix = name + "()"

    args = []
    if controls:
        args = nav_controls(prefix)

    kwargs: dict[str, Any] = {"id": name}
    if title:
        kwargs["title"] = nav_title(prefix)
    if sidebar:
        kwargs["sidebar"] = nav_sidebar(prefix)
    if headerfooter:
        header, footer = nav_headerfooter(prefix)
        kwargs["header"] = header
        kwargs["footer"] = footer

    return ui.TagList(ui.tags.h4(prefix), fn(*args, **kwargs))


app_ui = ui.page_navbar(
    *nav_controls("page_navbar"),
    # bg="#0062cc",
    # inverse=True,
    id="page_navbar",
    header="page_navbar(): Header",
    fillable=False,
    footer=ui.div(
        {"style": "width:80%;margin: 0 auto"},
        ui.tags.style(
            """
            h4 {
                margin-top: 3em;
            }
            """
        ),
        "page_navbar(): Footer (w/ custom styling)",
        make_navset(
            "navset_bar", ui.navset_bar, title=True, sidebar=True, headerfooter=True
        ),
        make_navset(
            "navset_bar", ui.navset_bar, title=True, sidebar=True, headerfooter=True
        ),
        make_navset("navset_tab", ui.navset_tab, headerfooter=True),
        make_navset("navset_pill", ui.navset_pill, headerfooter=True),
        make_navset("navset_underline", ui.navset_underline, headerfooter=True),
        make_navset(
            "navset_card_tab",
            ui.navset_card_tab,
            title=True,
            sidebar=True,
            headerfooter=True,
        ),
        make_navset(
            "navset_card_pill",
            ui.navset_card_pill,
            title=True,
            sidebar=True,
            headerfooter=True,
        ),
        make_navset(
            "navset_card_underline",
            ui.navset_card_underline,
            title=True,
            sidebar=True,
            headerfooter=True,
        ),
        make_navset("navset_pill_list", ui.navset_pill_list, headerfooter=True),
    ),
    title=nav_title("page_navbar()"),
    sidebar=nav_sidebar("page_navbar()"),
)


app = App(app_ui, None)
