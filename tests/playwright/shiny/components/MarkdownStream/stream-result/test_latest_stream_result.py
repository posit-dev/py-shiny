from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_latest_stream_result(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    stream = page.locator("#stream_id")
    stream_result = controller.OutputCode(page, "stream_result")
    stream_result.expect_value("")

    btn = controller.InputActionButton(page, "do_stream")
    btn.click()

    expect(stream).to_contain_text("Hello world!")
    stream_result.expect_value("Stream result: Hello world!")
