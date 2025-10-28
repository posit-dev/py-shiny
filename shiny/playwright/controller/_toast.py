from __future__ import annotations

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

from .._types import PatternOrStr, Timeout
from ..expect._internal import (
    expect_attribute_to_have_value as _expect_attribute_to_have_value,
)
from ._base import UiBase


class Toast(UiBase):
    """
    Controller for :func:`shiny.ui.toast`.

    Toast notifications are temporary, non-intrusive messages that appear on screen.
    """

    loc: Locator
    """
    Playwright `Locator` for the toast element.
    """
    loc_body: Locator
    """
    Playwright `Locator` for the toast body content.
    """
    loc_header: Locator
    """
    Playwright `Locator` for the toast header.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the Toast class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the toast notification.
        """
        super().__init__(page, id=id, loc=f".toast#{id}")
        self.loc_body = self.loc.locator(".toast-body")
        self.loc_header = self.loc.locator(".toast-header")

    def expect_visible(self, *, timeout: Timeout = None) -> None:
        """
        Expects the toast to be visible.

        Parameters
        ----------
        timeout
            The maximum time to wait for the toast to be visible. Defaults to `None`.
        """
        playwright_expect(self.loc).to_be_visible(timeout=timeout)

    def expect_hidden(self, *, timeout: Timeout = None) -> None:
        """
        Expects the toast to be hidden.

        Parameters
        ----------
        timeout
            The maximum time to wait for the toast to be hidden. Defaults to `None`.
        """
        playwright_expect(self.loc).to_be_hidden(timeout=timeout)

    def expect_body(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the toast body to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_body).to_have_text(value, timeout=timeout)

    def expect_header(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the toast header to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_header).to_have_text(value, timeout=timeout)

    def expect_type(self, value: str, *, timeout: Timeout = None) -> None:
        """
        Expects the toast to have the specified type class.

        Parameters
        ----------
        value
            The expected type (e.g., "success", "danger", "info", "warning").
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            loc=self.loc,
            timeout=timeout,
            name="class",
            value=f"text-bg-{value}",
        )

    def expect_position(self, value: str, *, timeout: Timeout = None) -> None:
        """
        Expects the toast's container to be in the specified position.

        Parameters
        ----------
        value
            The expected position (e.g., "top-left", "bottom-right").
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        # Toast container has the position in data attribute
        container = self.page.locator(f"[data-bslib-toast-container='{value}']")
        playwright_expect(container).to_be_attached(timeout=timeout)
        # Verify the toast is within this container
        toast_in_container = container.locator(f"#{self.id}")
        playwright_expect(toast_in_container).to_be_attached(timeout=timeout)

    def expect_autohide(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expects the toast to have the specified autohide setting.

        Parameters
        ----------
        value
            `True` if autohide is expected to be enabled, `False` otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        expected_value = "true" if value else "false"
        _expect_attribute_to_have_value(
            loc=self.loc,
            timeout=timeout,
            name="data-bs-autohide",
            value=expected_value,
        )
