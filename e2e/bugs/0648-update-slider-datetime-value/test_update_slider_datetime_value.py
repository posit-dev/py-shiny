from conftest import ShinyAppProc
from controls import InputActionButton, OutputTextVerbatim
from playwright.sync_api import Page


def test_slider_app(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    btn_reset = InputActionButton(page, "reset")
    out_txt = OutputTextVerbatim(page, "txt")

    out_txt.expect_value("2023-07-01 00:00:00")
    btn_reset.loc.click()
    out_txt.expect_value("2023-07-01 01:00:00")
