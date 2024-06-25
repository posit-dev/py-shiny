# See https://github.com/microsoft/playwright-python/issues/1532
# pyright: reportUnknownMemberType=false

from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_async_app(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    controller.InputTextArea(page, "value").set("Hello\nGoodbye")
    controller.InputActionButton(page, "go").click()

    # TODO-future; Make into proper class
    progress = page.locator("#shiny-notification-panel")
    expect(progress).to_be_visible()
    expect(progress).to_contain_text("Calculating...")

    controller.OutputTextVerbatim(page, "hash_output").expect_value(
        "2e220fb9d401bf832115305b9ae0277e7b8b1a9368c6526e450acd255e0ec0c2", timeout=2000
    )

    expect(progress).to_be_hidden()
