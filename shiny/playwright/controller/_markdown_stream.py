from __future__ import annotations

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

from .._types import PatternOrStr, Timeout
from ._base import UiBase


class MarkdownStream(UiBase):
    """Controller for :func:`shiny.ui.MarkdownStream`."""

    loc: Locator
    """
    Playwright `Locator` for the markdown stream.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `MarkdownStream` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the chat.
        """
        super().__init__(
            page,
            id=id,
            loc=f"#{id}",
        )

    def expect_content(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the content of the markdown stream to match a value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            Maximum time in milliseconds to wait for the content to match the value.
        """
        playwright_expect(self.loc).to_have_text(value, timeout=timeout)
