from playwright.sync_api import Page
from playwright.sync_api import expect as playwright_expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_action_link_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    default = controller.InputActionLink(page, "default")
    default.expect_label("Default action link")
    playwright_expect(default.loc.locator("svg.fa")).to_have_count(0)
    controller.OutputCode(page, "default_txt").expect_value("Link clicked 0 times")
    default.click()
    controller.OutputCode(page, "default_txt").expect_value("Link clicked 1 times")

    icon = controller.InputActionLink(page, "icon")
    playwright_expect(icon.loc.locator("svg.fa")).to_have_count(1)
