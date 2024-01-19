from __future__ import annotations

import typing

from controls import (
    Accordion,
    Card,
    LayoutNavsetTab,
    OutputDataFrame,
    OutputTextVerbatim,
    Sidebar,
)
from playwright.sync_api import Page, expect

from shiny import ui
from shiny.express import ui as xui


def verify_express_accordion(page: Page) -> None:
    acc = Accordion(page, "express_accordion")
    acc_panel_2 = acc.accordion_panel("Panel 2")
    acc_panel_2.expect_open(True)
    acc_panel_2.expect_body("n = 50")
    acc_panel_2.set(False)
    acc_panel_2.expect_open(False)


def compare_annotations(
    ui_fn: typing.Callable[..., typing.Any], layout_fn: typing.Callable[..., typing.Any]
) -> None:
    ui_a = ui_fn.__annotations__
    layout_a = layout_fn.__annotations__
    keys: list[str] = []
    for key, _ in ui_a.items():
        keys.append(key)
    for key, _ in layout_a.items():
        if key not in keys:
            keys.append(key)
    for key in keys:
        if key == "args":
            assert key in ui_a
            assert key not in layout_a
        elif key == "return":
            ui_val = ui_a[key]
            layout_val = (
                layout_a[key].replace("RecallContextManager[", "").replace("]", "")
            )
            assert layout_val.endswith(ui_val)
        else:
            assert ui_a[key] == layout_a[key]


def verify_express_page_default(page: Page) -> None:
    nav_html = LayoutNavsetTab(page, "express_navset_tab")
    nav_html.expect_content("pre 0pre 1pre 2")
    nav_html.set("div")
    nav_html.expect_content("div 0\ndiv 1\ndiv 2")
    nav_html.set("span")
    nav_html.expect_content("span 0span 1span 2")
    navset_card_tab = LayoutNavsetTab(page, "express_navset_card_tab")
    navset_card_tab.expect_content("")
    # since it is a custom table we can't use the OutputTable controls
    shell_text = page.locator("#shell").inner_text().strip()
    assert shell_text == (
        "R1C1R1\nR1C1R2-R1C1R1\nR1C1R2-R1C1R2\nR1C1R2-R1C2\nR1C2"
    ), "Locator contents don't match expected text"


def verify_express_page_fillable(page: Page) -> None:
    card = Card(page, "card")
    output_txt = OutputTextVerbatim(page, "txt")
    output_txt.expect_value("50")
    bounding_box = card.loc.bounding_box()
    assert bounding_box is not None
    assert bounding_box["height"] > 300


def verify_express_page_fluid(page: Page) -> None:
    card = Card(page, "card")
    output_txt = OutputTextVerbatim(page, "txt")
    output_txt.expect_value("50")
    bounding_box = card.loc.bounding_box()
    assert bounding_box is not None
    assert bounding_box["height"] < 300


def verify_express_page_sidebar(page: Page) -> None:
    sidebar = Sidebar(page, "sidebar")
    sidebar.expect_text("SidebarTitle Sidebar Content")
    output_txt = OutputTextVerbatim(page, "txt")
    output_txt.expect_value("50")
    compare_annotations(ui.sidebar, xui.sidebar)


def verify_express_dataframe(page: Page) -> None:
    dataframe = OutputDataFrame(page, "sample_data_frame")
    dataframe.expect_n_row(6)


def verify_express_folium_render(page: Page) -> None:
    expect(page.get_by_text("Static Map")).to_have_count(1)
    expect(page.get_by_text("Map inside of render express call")).to_have_count(1)
    # map inside the @render.express
    expect(
        page.frame_locator("iframe").nth(1).get_by_role("link", name="OpenStreetMap")
    ).to_have_count(1)
    # map outside of the @render.express at the top level
    expect(
        page.frame_locator("iframe")
        .nth(0)
        .get_by_role("link", name="U.S. Geological Survey")
    ).to_have_count(1)
