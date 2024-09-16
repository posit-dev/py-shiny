from __future__ import annotations

import re

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

from .._types import PatternOrStr, Timeout
from ..expect._internal import (
    expect_attribute_to_have_value as _expect_attribute_to_have_value,
)
from ._base import InitLocator, UiBase


class _OverlayBase(UiBase):
    """Base class for overlay controls"""

    loc_trigger: Locator
    """
    Playwright `Locator` for the trigger element.
    """
    loc_overlay_body: Locator
    """
    Playwright `Locator` for the overlay body.
    """
    loc_overlay_container: Locator
    """
    Playwright `Locator` for of the overlay container.
    """

    def __init__(
        self,
        page: Page,
        *,
        id: str,
        loc: InitLocator,
        overlay_name: str,
        overlay_selector: str,
    ) -> None:
        """
        Initializes a new instance of the `OverlayBase` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the overlay.
        loc
            Playwright `Locator` of the overlay.
        overlay_name
            The name of the overlay.
        overlay_selector
            The selector of the overlay.
        """
        super().__init__(page, id=id, loc=loc)
        self._overlay_name = overlay_name
        self._overlay_selector = overlay_selector
        self.loc_trigger = self.loc.locator(
            f" > :last-child[data-bs-toggle='{self._overlay_name}']"
        )

    def _get_overlay_id(self, *, timeout: Timeout = None) -> str | None:
        """Note. This requires 2 steps. Will not work if the overlay element is rapidly created during locator fetch"""
        loc_el = self.loc.locator(
            f" > :last-child[data-bs-toggle='{self._overlay_name}']"
        )
        loc_el.wait_for(state="visible", timeout=timeout)
        loc_el.scroll_into_view_if_needed(timeout=timeout)
        return loc_el.get_attribute("aria-describedby")

    # @property
    # def loc_overlay_body(self) -> Locator:
    #     # Can not leverage `self.loc_overlay_container` as `self._overlay_selector` must
    #     # be concatenated directly to the result of `self._get_overlay_id()`
    #     return self.page.locator(f"#{self._get_overlay_id()}{self._overlay_selector}")

    # @property
    # def loc_overlay_container(self) -> Locator:
    #     return self.page.locator(f"#{self._get_overlay_id()}")

    def get_loc_overlay_body(self, *, timeout: Timeout = None) -> Locator:
        # Can not leverage `self.loc_overlay_container` as `self._overlay_selector` must
        # be concatenated directly to the result of `self._get_overlay_id()`
        return self.page.locator(
            f"#{self._get_overlay_id(timeout=timeout)}{self._overlay_selector}"
        )

    def get_loc_overlay_container(self, *, timeout: Timeout = None) -> Locator:
        """
        Returns the locator for the overlay container.

        Parameters
        ----------
        timeout
            The maximum time to wait for the overlay container to appear. Defaults to `None`.
        """
        return self.page.locator(f"#{self._get_overlay_id(timeout=timeout)}")

    def expect_body(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the overlay body to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the overlay body to appear. Defaults to `None`.
        """
        playwright_expect(self.get_loc_overlay_body(timeout=timeout)).to_have_text(
            value, timeout=timeout
        )

    def expect_active(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expects the overlay to be active or inactive.

        Parameters
        ----------
        value
            `True` if the overlay is expected to be active, False otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        attr_value = re.compile(r".*") if value else None
        return _expect_attribute_to_have_value(
            loc=self.loc_trigger,
            timeout=timeout,
            name="aria-describedby",
            value=attr_value,
        )

    def expect_placement(self, value: str, *, timeout: Timeout = None) -> None:
        """
        Expects the overlay to have the specified placement.

        Parameters
        ----------
        value
            The expected placement value.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        return _expect_attribute_to_have_value(
            loc=self.get_loc_overlay_container(timeout=timeout),
            timeout=timeout,
            name="data-popper-placement",
            value=value,
        )


class Popover(_OverlayBase):
    """Controller for :func:`shiny.ui.popover`."""

    loc_trigger: Locator
    """
    Playwright `Locator` for the trigger element that opens/closes the popover.
    """
    loc_overlay_body: Locator
    """
    Playwright `Locator` for the popover body.
    """
    loc_overlay_container: Locator
    """
    Playwright `Locator` for the popover container.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `Popover` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the popover.
        """
        super().__init__(
            page,
            id=id,
            loc=f"bslib-popover#{id}",
            overlay_name="popover",
            overlay_selector=".popover > div.popover-body",
        )

    def set(self, open: bool, timeout: Timeout = None) -> None:
        """
        Sets the state of the popover.

        Parameters
        ----------
        open
            `True` to open the popover and `False` to close it.
        timeout
            The maximum time to wait for the popover to be visible and interactable. Defaults to `None`.
        """
        if open ^ self.get_loc_overlay_body(timeout=timeout).count() > 0:
            self._toggle(timeout=timeout)

    def _toggle(self, timeout: Timeout = None) -> None:
        """
        Toggles the state of the popover.

        Parameters
        ----------
        timeout
            The maximum time to wait for the popover to be visible and interactable. Defaults to `None`.
        """
        self.loc_trigger.wait_for(state="visible", timeout=timeout)
        self.loc_trigger.scroll_into_view_if_needed(timeout=timeout)
        self.loc_trigger.click(timeout=timeout)

    def expect_title(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the popover title to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the popover header to appear. Defaults to `None`.
        """
        playwright_expect(
            self.get_loc_overlay_container().locator("> .popover-header")
        ).to_have_text(value, timeout=timeout)


class Tooltip(_OverlayBase):
    """Controller for :func:`shiny.ui.tooltip`."""

    loc_container: Locator
    """
    Playwright `Locator` for the container tooltip.
    """
    loc: Locator
    """
    Playwright `Locator` for the tooltip content.
    """
    loc_trigger: Locator
    """
    Playwright `Locator` for the trigger element.
    """
    loc_overlay_body: Locator
    """
    Playwright `Locator` for the overlay body.
    """
    loc_overlay_container: Locator
    """
    Playwright `Locator` for the overlay container.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `Tooltip` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the tooltip.
        """
        super().__init__(
            page,
            id=id,
            loc=f"bslib-tooltip#{id}",
            overlay_name="tooltip",
            overlay_selector=".tooltip > div.tooltip-inner",
        )

    def set(self, open: bool, timeout: Timeout = None) -> None:
        """
        Sets the state of the tooltip.

        Parameters
        ----------
        open
            `True` to open the tooltip and `False` to close it.
        timeout
            The maximum time to wait for the tooltip to be visible and interactable. Defaults to `None`.
        """
        if open ^ self.get_loc_overlay_body(timeout=timeout).count() > 0:
            self._toggle(timeout=timeout)
        if not open:
            self.get_loc_overlay_body(timeout=timeout).click()

    def _toggle(self, timeout: Timeout = None) -> None:
        """
        Toggles the state of the tooltip.

        Parameters
        ----------
        timeout
            The maximum time to wait for the tooltip to be visible and interactable. Defaults to `None`.
        """
        self.loc_trigger.wait_for(state="visible", timeout=timeout)
        self.loc_trigger.scroll_into_view_if_needed(timeout=timeout)
        self.loc_trigger.hover(timeout=timeout)
