from __future__ import annotations

import re
from typing import Literal

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

from .._types import PatternOrStr, Timeout
from ..expect._internal import (
    expect_attribute_to_have_value as _expect_attribute_to_have_value,
)
from ..expect._internal import expect_class_to_have_value as _expect_class_to_have_value
from ._base import InitLocator, UiBase

_PLACEMENT_BS: dict[str, str] = {
    "right": "end",
    "end": "end",
    "left": "start",
    "start": "start",
    "top": "top",
    "bottom": "bottom",
}


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

    def _get_overlay_id(self, *, timeout: Timeout = None) -> str:
        """Note. This requires 2 steps. Will not work if the overlay element is rapidly created during locator fetch"""
        loc_el = self.loc.locator(
            f" > :last-child[data-bs-toggle='{self._overlay_name}']"
        )
        loc_el.wait_for(state="visible", timeout=timeout)
        loc_el.scroll_into_view_if_needed(timeout=timeout)
        playwright_expect(loc_el).to_have_attribute(
            "aria-describedby", re.compile(r".+"), timeout=timeout
        )
        overlay_id = loc_el.get_attribute("aria-describedby")
        assert overlay_id is not None
        return overlay_id

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

    def _is_active(self, *, timeout: Timeout = None) -> bool:
        return (
            self.loc_trigger.get_attribute("aria-describedby", timeout=timeout)
            is not None
        )

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
        _expect_attribute_to_have_value(
            loc=self.loc_trigger,
            timeout=timeout,
            name="aria-describedby",
            value=attr_value,
        )
        self.page.wait_for_function(
            """
            ([id, expected]) => {
                const overlay = document.getElementById(id);
                return overlay !== null && overlay.visible === expected;
            }
            """,
            arg=[self.id, value],
            timeout=timeout,
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
        if open != self._is_active(timeout=timeout):
            self._toggle(timeout=timeout)
        self.expect_active(open, timeout=timeout)

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
        is_active = self._is_active(timeout=timeout)
        if open and not is_active:
            self._toggle(timeout=timeout)
        elif not open and is_active:
            self.get_loc_overlay_body(timeout=timeout).click()
        self.expect_active(open, timeout=timeout)

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


class Offcanvas(UiBase):
    """Controller for :func:`shiny.ui.offcanvas`."""

    loc: Locator
    """
    Playwright `Locator` for the offcanvas root element (`bslib-offcanvas#{id}`).
    """
    loc_trigger: Locator
    """
    Playwright `Locator` for the trigger element(s) targeting this offcanvas panel.
    """
    loc_title: Locator
    """
    Playwright `Locator` for the title inside the offcanvas header.
    """
    loc_close: Locator
    """
    Playwright `Locator` for the close button inside the offcanvas header.
    """
    loc_body: Locator
    """
    Playwright `Locator` for the offcanvas body.
    """
    loc_footer: Locator
    """
    Playwright `Locator` for the offcanvas footer.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `Offcanvas` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the offcanvas.
        """
        super().__init__(page, id=id, loc=f"bslib-offcanvas#{id}")
        self.loc_trigger = self.page.locator(
            f"[data-bs-toggle='offcanvas'][data-bs-target='#{id}'], "
            f"[data-bs-toggle='offcanvas'][href='#{id}'], "
            f"[data-bs-toggle='offcanvas'][aria-controls='{id}']"
        )
        self.loc_title = self.loc.locator("header.offcanvas-header .offcanvas-title")
        self.loc_close = self.loc.locator(
            "header.offcanvas-header button.btn-close[data-bs-dismiss='offcanvas']"
        )
        self.loc_body = self.loc.locator("div.offcanvas-body")
        self.loc_footer = self.loc.locator("footer.offcanvas-footer")

    def open(self, *, timeout: Timeout = None) -> None:
        """
        Opens the offcanvas panel.

        Parameters
        ----------
        timeout
            The maximum time to wait for the offcanvas to open. Defaults to `None`.
        """
        self.set(open=True, timeout=timeout)

    def show(self, *, timeout: Timeout = None) -> None:
        """
        Shows (opens) the offcanvas panel.

        Alias for :meth:`~shiny.playwright.controller.Offcanvas.open`.

        Parameters
        ----------
        timeout
            The maximum time to wait for the offcanvas to open. Defaults to `None`.
        """
        self.open(timeout=timeout)

    def close(self, *, timeout: Timeout = None) -> None:
        """
        Closes the offcanvas panel.

        Parameters
        ----------
        timeout
            The maximum time to wait for the offcanvas to close. Defaults to `None`.
        """
        self.set(open=False, timeout=timeout)

    def set(self, open: bool, *, timeout: Timeout = None) -> None:
        """
        Sets the offcanvas panel to open or closed.

        Parameters
        ----------
        open
            `True` to open the offcanvas, `False` to close it.
        timeout
            The maximum time to wait for the offcanvas to change state. Defaults to `None`.
        """
        is_open = "show" in (self.loc.get_attribute("class") or "")
        if open and not is_open:
            self._open(timeout=timeout)
        elif not open and is_open:
            self._close(timeout=timeout)

    def _open(self, *, timeout: Timeout = None) -> None:
        """Opens the panel by clicking the trigger element."""
        self.loc_trigger.wait_for(state="visible", timeout=timeout)
        self.loc_trigger.scroll_into_view_if_needed(timeout=timeout)
        self.loc_trigger.click(timeout=timeout)

    def _close(self, *, timeout: Timeout = None) -> None:
        """Closes the panel by clicking the close button."""
        self.loc_close.wait_for(state="visible", timeout=timeout)
        self.loc_close.scroll_into_view_if_needed(timeout=timeout)
        self.loc_close.click(timeout=timeout)

    def expect_open(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expects the offcanvas panel to be open or closed.

        Parameters
        ----------
        value
            `True` if the offcanvas should be open, `False` if it should be closed.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc,
            "show",
            has_class=value,
            timeout=timeout,
        )

    def expect_title(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the offcanvas title to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the title to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_title).to_have_text(value, timeout=timeout)

    def expect_body(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the offcanvas body to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the offcanvas body to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_body).to_have_text(value, timeout=timeout)

    def expect_footer(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the offcanvas footer to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the footer to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_footer).to_have_text(value, timeout=timeout)

    def expect_placement(
        self,
        value: Literal["start", "end", "top", "bottom", "left", "right"],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the offcanvas panel to have the specified placement.

        Parameters
        ----------
        value
            The expected placement ("start", "end", "top", "bottom", "left", "right").
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        bs_val = _PLACEMENT_BS.get(value, value)
        _expect_class_to_have_value(
            self.loc,
            f"offcanvas-{bs_val}",
            has_class=True,
            timeout=timeout,
        )
