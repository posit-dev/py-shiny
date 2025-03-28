from pathlib import Path

import pytest
from playwright.sync_api import Page

from shiny.playwright.controller import InputRadioButtons, OutputCode
from shiny.run import ShinyAppProc, run_shiny_app


@pytest.mark.parametrize("app_name", ["app-attr.py", "app-global.py"])
def test_bookmark_modules(page: Page, app_name: str):

    app: ShinyAppProc = run_shiny_app(
        Path(__file__).parent / app_name,
        wait_for_start=True,
    )

    try:

        page.goto(app.url)

        called_saved = OutputCode(page, "called_saved")
        called_restored = OutputCode(page, "called_restored")
        called_saved.expect_value("False")
        called_restored.expect_value("False")

        letter = InputRadioButtons(page, "letter")
        letter.expect_selected("A")
        letter.set("B")

        called_saved.expect_value("True")
        called_restored.expect_value("False")

        page.reload()

        called_restored.expect_value("True")

        letter.expect_selected("B")
        assert "_state_id_" in page.url

    finally:
        app.close()
