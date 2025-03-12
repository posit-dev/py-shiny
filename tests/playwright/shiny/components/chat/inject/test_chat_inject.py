from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_inject(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    TIMEOUT = 30 * 1000

    chat = controller.Chat(page, "chat")
    expect(chat.loc).to_be_visible(timeout=TIMEOUT)

    chat.expect_latest_message(
        "Starting stream...injected chunk...stream complete",
        timeout=TIMEOUT,
    )

    btn = controller.InputActionButton(page, "run_test")
    expect(btn.loc).to_be_visible(timeout=TIMEOUT)
    btn.click()

    chat.expect_latest_message(
        "can inject chunks",
        timeout=TIMEOUT,
    )
