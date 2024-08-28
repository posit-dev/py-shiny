from __future__ import annotations

from playwright.sync_api import Page

from ._base import InputActionBase, WidthLocM


# TODO: Use mixin for dowloadlink and download button
class DownloadLink(InputActionBase):
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
        super().__init__(
            page,
            id=id,
            loc=f"#{id}.shiny-download-link:not(.btn)",
        )


class DownloadButton(
    WidthLocM,
    InputActionBase,
):
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
        super().__init__(
            page,
            id=id,
            loc=f"#{id}.btn.shiny-download-link",
        )
