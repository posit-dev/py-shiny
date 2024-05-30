from pathlib import Path

import pytest

from shiny.test import Page, ShinyAppProc
from shiny.test._conftest import run_shiny_app
from shiny.test._controls import Card, OutputCode, ValueBox


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

    card = Card(page, sel_card)
    vb = ValueBox(page, sel_vb)
    out_card = OutputCode(page, "out_card")
    out_vb = OutputCode(page, "out_value_box")

    # Open and close card full screen, check input value ------
    card.expect_full_screen_open(False)
    out_card.expect_value("False")

    card.open_full_screen()
    card.expect_full_screen_open(True)
    out_card.expect_value("True")

    card.close_full_screen()
    card.expect_full_screen_open(False)
    out_card.expect_value("False")

    # Open and close value box full screen, check input value ------
    vb.expect_full_screen_open(False)
    out_vb.expect_value("False")

    vb.open_full_screen()
    vb.expect_full_screen_open(True)
    out_vb.expect_value("True")

    vb.close_full_screen()
    vb.expect_full_screen_open(False)
    out_vb.expect_value("False")
