from __future__ import annotations

from typing import Literal

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

from .._types import PatternOrStr, Timeout
from ..expect._internal import expect_class_to_have_value as _expect_class_to_have_value
from ._base import UiWithContainer, WidthLocM


class Sidebar(
    WidthLocM,
    UiWithContainer,
):
    """Controller for :func:`shiny.ui.sidebar`."""

    loc_container: Locator
    """
    Playwright `Locator` for the sidebar layout.
    """
    loc: Locator
    """
    Playwright `Locator` for the sidebar.
    """
    loc_handle: Locator
    """
    Playwright `Locator` for the open/close handle of the sidebar.
    """
    loc_position: Locator
    """
    Playwright `Locator` for the position of the sidebar.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a sidebar control.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the sidebar.
        """
        super().__init__(
            page,
            id=id,
            loc=f"> aside#{id}",
            loc_container="div.bslib-sidebar-layout",
        )
        self.loc_handle = self.loc_container.locator("button.collapse-toggle")
        self.loc_position = self.loc.locator("..")

    def expect_text(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Asserts that the sidebar has the expected text.

        Parameters
        ----------
        value
            The expected text in the sidebar.
        timeout
            The maximum time to wait for the text to appear. Defaults to `None`.
        """
        playwright_expect(self.loc).to_have_text(value, timeout=timeout)

    def expect_position(
        self,
        value: Literal["left", "right"],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the sidebar is in the expected position.

        Parameters
        ----------
        value
            The expected position of the sidebar.
        timeout
            The maximum time to wait for the sidebar to appear. Defaults to `None`.
        """
        is_right_sidebar = value == "right"
        _expect_class_to_have_value(
            self.loc_position,
            f"sidebar-{value}",
            has_class=is_right_sidebar,
            timeout=timeout,
        )

    def expect_handle(self, exists: bool, *, timeout: Timeout = None) -> None:
        """
        Asserts that the sidebar handle exists or does not exist.

        Parameters
        ----------
        exists
            `True` if the sidebar open/close handle should exist, `False` otherwise.
        timeout
            The maximum time to wait for the sidebar handle to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_handle).to_have_count(int(exists), timeout=timeout)

    def expect_open(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the sidebar to be open or closed.

        Parameters
        ----------
        value
            `True` if the sidebar should be open, `False` to be closed.
        timeout
            The maximum time to wait for the sidebar to open or close. Defaults to `None`.
        """
        playwright_expect(self.loc_handle).to_have_attribute(
            "aria-expanded", str(value).lower(), timeout=timeout
        )

    def set(self, open: bool, *, timeout: Timeout = None) -> None:
        """
        Sets the sidebar to be open or closed.

        Parameters
        ----------
        open
            `True` to open the sidebar and `False` to close it.
        timeout
            The maximum time to wait for the sidebar to open or close. Defaults to `None`.
        """
        if open ^ (self.loc_handle.get_attribute("aria-expanded") == "true"):
            self._toggle(timeout=timeout)

    def _toggle(self, *, timeout: Timeout = None) -> None:
        """
        Toggles the sidebar open or closed.

        Parameters
        ----------
        timeout
            The maximum time to wait for the sidebar to toggle. Defaults to `None`.
        """
        self.loc_handle.wait_for(state="visible", timeout=timeout)
        self.loc_handle.scroll_into_view_if_needed(timeout=timeout)
        self.loc_handle.click(timeout=timeout)
