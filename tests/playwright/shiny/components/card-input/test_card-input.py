from pathlib import Path

import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc, run_shiny_app


@pytest.mark.parametrize(
    "app_path, sel_card, sel_vb",
    [
        ("app-express.py", "my_card", "my_value_box"),
        ("app-module.py", "card-thing", "value_box-thing"),
    ],
)
def test_card_input(page: Page, app_path: str, sel_card: str, sel_vb: str) -> None:
    sa: ShinyAppProc = run_shiny_app(
        Path(__file__).parent / app_path, wait_for_start=True
    )

    page.goto(sa.url)

    card = controller.Card(page, sel_card)
    vb = controller.ValueBox(page, sel_vb)
    out_card = controller.OutputCode(page, "out_card")
    out_vb = controller.OutputCode(page, "out_value_box")

    # Open and close card full screen, check input value ------
    card.expect_full_screen(False)
    out_card.expect_value("False")

    card.set_full_screen(True)
    card.expect_full_screen(True)
    out_card.expect_value("True")

    card.set_full_screen(False)
    card.expect_full_screen(False)
    out_card.expect_value("False")

    # Open and close value box full screen, check input value ------
    vb.expect_full_screen(False)
    out_vb.expect_value("False")

    vb.set_full_screen(True)
    vb.expect_full_screen(True)
    out_vb.expect_value("True")

    vb.set_full_screen(False)
    vb.expect_full_screen(False)
    out_vb.expect_value("False")
