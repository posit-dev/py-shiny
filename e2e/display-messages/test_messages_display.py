from conftest import ShinyAppProc, create_doc_example_fixture
from playwright.sync_api import Page, expect
from playwright.async_api import async_playwright
from controls import ActionButton, Modal, Notification, Progress
import pytest

modal_app = create_doc_example_fixture("modal")
notifications_app = create_doc_example_fixture("notification_show")
progress_app = create_doc_example_fixture("Progress")


def test_modal(page: Page, modal_app: ShinyAppProc):
    page.goto(modal_app.url)

    show_btn = ActionButton(page, "show")
    show_btn.loc.click()

    modal = Modal(page)
    expect(modal.loc).to_be_visible()

    expect(modal.modal_content).to_be_visible()
    expect(modal.modal_header).to_have_text("Somewhat important message")
    expect(modal.modal_body).to_have_text("This is a somewhat important message.")

    # Verify modal is closed (with easy_close being True) with a key press
    page.keyboard.press("Escape")
    expect(modal.loc).not_to_be_visible()

    #TODO: (additional) Add check for modal_remove and modal_button

def test_notification(page: Page, notifications_app: ShinyAppProc):
    page.goto(notifications_app.url)

    show_btn = ActionButton(page, "show")
    remove_btn = ActionButton(page, "remove")
    notification = Notification(page)

    show_btn.loc.click()
    expect(notification.loc).to_be_visible()

    expect(notification.notification_content).to_be_visible()
    expect(notification.notification_content_text).to_have_text("Message 0")
    expect(notification.notification_close).to_be_visible()

    # close notification with x option
    notification.notification_close.click()
    expect(notification.loc).not_to_be_visible()

    # Show notification for second time
    show_btn.loc.click()
    expect(notification.loc).to_be_visible()
    expect(notification.notification_content_text).to_have_text("Message 1")

    # close notification with Remove option
    remove_btn.loc.click()
    expect(notification.loc).not_to_be_visible()

def test_progress(page: Page, progress_app: ShinyAppProc):
    page.goto(progress_app.url)

    compute_btn = ActionButton(page, "button")
    progress = Progress(page)

    compute_btn.loc.click()
    expect(progress.progress_notification).to_be_visible()

    #TODO: Handle async with pytest
        # Ref: https://github.com/pytest-dev/pytest/issues/7110
        # Ref: https://stackoverflow.com/questions/55893235/pytest-skips-test-saying-asyncio-not-installed

    # async with async_playwright() as playwright
    #     await expect(progress.progress_status).to_have_class("active")
    #     await expect(progress.progress_text_message).to_have_text("Computing")
    #     await expect(progress.progress_text_detail).to_have_text("This may take a while...")



