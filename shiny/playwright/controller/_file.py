from __future__ import annotations

from playwright.sync_api import Page

from ._base import InputActionBase, WidthLocM


class _DownloadMixin(WidthLocM, InputActionBase):
    """Mixin for download controls."""

    def __init__(self, page: Page, id: str, *, loc_suffix: str) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"#{id}.shiny-download-link{loc_suffix}",
        )


class DownloadLink(_DownloadMixin):
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


class DownloadButton(_DownloadMixin):
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
