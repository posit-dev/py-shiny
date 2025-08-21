from typing import Union

import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


@pytest.mark.parametrize(
    "nav_factory,nav_id,out_id",
    [
        (controller.NavsetPill, "selected_navset_pill", "_"),
        (controller.NavsetUnderline, "selected_navset_underline", "_underline"),
    ],
    ids=["pill", "underline"],
)
def test_navset_menu(
    page: Page,
    app: ShinyAppProc,
    nav_factory: Union[type[controller.NavsetPill], type[controller.NavsetUnderline]],
    nav_id: str,
    out_id: str,
):

    page.goto(app.url)
    navset = nav_factory(page, nav_id)
    output: controller.OutputText = controller.OutputText(page, out_id)

    navset.expect_value("A")
    output.expect_value("A")

    for panel in ["B", "C", "D"]:
        navset.set(panel)
        navset.expect_value(panel)
        output.expect_value(panel)
