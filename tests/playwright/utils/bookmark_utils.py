from __future__ import annotations

from playwright.sync_api import Page

__all__ = ("load_bookmark_url",)


def load_bookmark_url(page: Page) -> None:
    """
    Load the page's current (bookmarked) URL in a fresh page load.

    Use this instead of `page.reload()` when asserting that bookmarked state is
    restored. A reload lets the browser restore the previous form control values
    (Firefox does this), which then overwrite the values Shiny restores from the
    bookmark URL. Navigating anew starts from the markup the server sends, so the
    assertions actually exercise bookmark restoration.
    """
    page.goto(page.url)
