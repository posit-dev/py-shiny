from playwright.sync_api import Page


def wait_for_url_change(page: Page, existing_url: str, timeout: int = 5000):
    page.wait_for_url(lambda url: url != existing_url, timeout=timeout)
