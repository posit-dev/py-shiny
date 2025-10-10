from __future__ import annotations

from playwright.sync_api import Page
from playwright.sync_api import expect as playwright_expect

from .._types import PatternOrStr, Timeout
from ._base import InputActionBase, WidthLocStyleM


class _DownloadBase(
    WidthLocStyleM,
    InputActionBase,
):
    """Mixin for download controls."""

    def __init__(self, page: Page, id: str, *, loc_suffix: str) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"#{id}.shiny-download-link{loc_suffix}",
        )

    def expect_label(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """Expect the anchor itself to contain the provided label text."""

        playwright_expect(self.loc).to_have_text(value, timeout=timeout)


class DownloadLink(_DownloadBase):
    """
    Controller for :func:`shiny.ui.download_link`.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `DownloadLink` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the download link.
        """
        super().__init__(page, id=id, loc_suffix=":not(.btn)")


class DownloadButton(_DownloadBase):
    """
    Controller for :func:`shiny.ui.download_button`
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `DownloadButton` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the download button.
        """
        super().__init__(page, id=id, loc_suffix=".btn")
