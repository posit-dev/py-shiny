from __future__ import annotations

from typing import Protocol

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

from .._types import PatternOrStr, StyleValue, Timeout
from ..expect._internal import expect_style_to_have_value as _expect_style_to_have_value
from ._base import OutputBaseP, UiBaseP, UiWithContainer, WidthLocM


class _CardBodyP(UiBaseP, Protocol):
    """
    Represents the body of a card control.
    """

    loc_body: Locator
    """
    Playwright `Locator` for the body element of the card control.
    """


class _CardBodyM:
    """Represents a card body element with additional methods for testing."""

    def expect_body(
        self: _CardBodyP,
        value: PatternOrStr | list[PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
        """Expect the card body element to have the specified text.

        Parameters
        ----------
        value
            The expected text or a list of expected texts.
        timeout
            The maximum time to wait for the text to appear. Defaults to `None`.
        """
        playwright_expect(self.loc).to_have_text(
            value,
            timeout=timeout,
        )


class _CardFooterLayoutP(UiBaseP, Protocol):
    """
    Represents the layout of the footer in a card.
    """

    loc_footer: Locator
    """
    Playwright `Locator` for the footer element.
    """


class _CardFooterM:
    """
    Represents the footer section of a card.
    """

    def expect_footer(
        self: _CardFooterLayoutP,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the footer section of the card has the expected text.

        Parameters
        ----------
        value
            The expected text in the footer section.
        timeout
            The maximum time to wait for the footer text to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_footer).to_have_text(
            value,
            timeout=timeout,
        )


class _CardValueBoxFullScreenLayoutP(OutputBaseP, Protocol):
    """
    Represents a card / Value Box full-screen layout for the Playwright controls.
    """

    loc_title: Locator
    """
    Playwright `Locator` for the title element.
    """
    _loc_fullscreen: Locator
    """
    Playwright `Locator` for the full-screen element.
    """
    _loc_close_button: Locator
    """
    Playwright `Locator` for the close button element.
    """


class _CardValueBoxFullScreenM:
    """
    Represents a class for managing full screen functionality of a Card or Value Box.
    """

    def set_full_screen(
        self: _CardValueBoxFullScreenLayoutP, open: bool, *, timeout: Timeout = None
    ) -> None:
        """
        Sets the element to full screen mode or exits full screen mode.

        Parameters
        ----------
        open
            `True` to open the element in full screen mode, `False` to exit full screen mode.
        timeout
            The maximum time to wait for the operation to complete. Defaults to `None`.
        """
        if open:
            self.loc_title.hover(timeout=timeout)
            self._loc_fullscreen.wait_for(state="visible", timeout=timeout)
            self._loc_fullscreen.click(timeout=timeout)
        else:
            self._loc_close_button.click(timeout=timeout)

    def expect_full_screen(
        self: _CardValueBoxFullScreenLayoutP, value: bool, *, timeout: Timeout = None
    ) -> None:
        """
        Verifies if the full screen mode is currently open.

        Parameters
        ----------
        value
            `True` if the item is to be in full screen mode, `False` otherwise.
        timeout
            The maximum time to wait for the verification. Defaults to `None`.
        """
        playwright_expect(self._loc_close_button).to_have_count(
            int(value), timeout=timeout
        )

    def expect_full_screen_available(
        self: _CardValueBoxFullScreenLayoutP,
        value: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects whether full screen mode is available for the element.

        Parameters
        ----------
        value
            `True` if the element is expected to be available for full screen mode, False otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self._loc_fullscreen).to_have_count(
            int(value), timeout=timeout
        )


class ValueBox(
    WidthLocM,
    _CardValueBoxFullScreenM,
    UiWithContainer,
):
    """
    Controller for :func:`shiny.ui.value_box`.
    """

    loc: Locator
    """
    Playwright `Locator` for the value box's value.
    """
    loc_showcase: Locator
    """
    Playwright `Locator` for the value box showcase.
    """
    loc_title: Locator
    """
    Playwright `Locator` for the value box title.
    """
    loc_body: Locator
    """
    Playwright `Locator` for the value box body.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `ValueBox` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the value box.

        """
        super().__init__(
            page,
            id=id,
            loc_container=f"div#{id}.bslib-value-box",
            loc="> div.card-body > .value-box-grid, > div.card-body",
        )
        value_box_grid = self.loc
        self.loc_showcase = value_box_grid.locator("> .value-box-showcase")
        self.loc_title = value_box_grid.locator("> .value-box-area > .value-box-title")
        self.loc = value_box_grid.locator("> .value-box-area > .value-box-value")
        self.loc_body = value_box_grid.locator(
            "> .value-box-area > :not(.value-box-title, .value-box-value)"
        )
        self._loc_fullscreen = self.loc_container.locator(
            "> bslib-tooltip > .bslib-full-screen-enter"
        )

        # an easier approach is using `#bslib-full-screen-overlay:has(+ div#{id}.card) > a`
        # but playwright doesn't allow that
        self._loc_close_button = (
            self.page.locator(f"#bslib-full-screen-overlay + div#{id}.bslib-value-box")
            .locator("..")
            .locator("#bslib-full-screen-overlay > a")
        )

    def expect_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expects the value box to have a specific height.

        Parameters
        ----------
        value
            The expected height value.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_style_to_have_value(
            self.loc_container, "height", value, timeout=timeout
        )

    def expect_max_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expects the value box to have a specific maximum height.

        Parameters
        ----------
        value
            The expected maximum height value.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_style_to_have_value(
            self.loc_container, "max-height", value, timeout=timeout
        )

    def expect_title(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the value box title to have a specific text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.

        """
        playwright_expect(self.loc_title).to_have_text(
            value,
            timeout=timeout,
        )

    def expect_value(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the value box value to have a specific text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc).to_have_text(
            value,
            timeout=timeout,
        )

    def expect_body(
        self,
        value: PatternOrStr | list[PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the value box body to have specific text.

        Parameters
        ----------
        value
            The expected text pattern or list of patterns/strings.

            Note: If testing against multiple elements, text should be an array.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_body).to_have_text(
            value,
            timeout=timeout,
        )


class Card(
    WidthLocM,
    _CardFooterM,
    _CardBodyM,
    _CardValueBoxFullScreenM,
    UiWithContainer,
):
    """
    Controller for :func:`shiny.ui.card`.
    """

    loc_container: Locator
    """
    Playwright `Locator` for the card container.
    """
    loc: Locator
    """
    Playwright `Locator` for the card's value.
    """
    loc_title: Locator
    """
    Playwright `Locator` for the card title.
    """
    loc_footer: Locator
    """
    Playwright `Locator` for the card footer.
    """
    loc_body: Locator
    """
    Playwright `Locator` for the card body.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `Card` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the card.
        """
        super().__init__(
            page,
            id=id,
            loc_container=f"div#{id}.card",
            loc="> div.card-body",
        )
        self.loc_title = self.loc_container.locator("> div.card-header")
        self.loc_footer = self.loc_container.locator("> div.card-footer")
        self._loc_fullscreen = self.loc_container.locator(
            "> bslib-tooltip > .bslib-full-screen-enter"
        )
        # an easier approach is using `#bslib-full-screen-overlay:has(+ div#{id}.card) > a`
        # but playwright doesn't allow that
        self._loc_close_button = (
            self.page.locator(f"#bslib-full-screen-overlay + div#{id}")
            .locator("..")
            .locator("#bslib-full-screen-overlay > a")
        )
        self.loc_body = self.loc

    def expect_header(
        self,
        value: PatternOrStr | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the card header to have a specific text.

        Parameters
        ----------
        value
            The expected text pattern or string.

            Note: `None` if the header is expected to not exist.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if value is None:
            playwright_expect(self.loc_title).to_have_count(0, timeout=timeout)
        else:
            playwright_expect(self.loc_title).to_have_text(value, timeout=timeout)

    # def expect_body(
    #     self,
    #     text: PatternOrStr,
    #     index: int = 0,
    #     *,
    #     timeout: Timeout = None,
    # ) -> None:
    #     """Note: Function requires an index since multiple bodies can exist in loc"""
    #     playwright_expect(self.loc.nth(index).locator("> :first-child")).to_have_text(
    #         text,
    #         timeout=timeout,
    #     )

    def expect_footer(
        self,
        value: PatternOrStr | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the card footer to have a specific text.

        Parameters
        ----------
        value
            The expected text pattern or string
            Note: None if the footer is expected to not exist.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if value is None:
            playwright_expect(self.loc_footer).to_have_count(0, timeout=timeout)
        else:
            playwright_expect(self.loc_footer).to_have_text(value, timeout=timeout)

    def expect_max_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expects the card to have a specific maximum height.

        Parameters
        ----------
        value
            The expected maximum height value.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_style_to_have_value(
            self.loc_container, "max-height", value, timeout=timeout
        )

    def expect_min_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expects the card to have a specific minimum height.

        Parameters
        ----------
        value
            The expected minimum height value.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_style_to_have_value(
            self.loc_container, "min-height", value, timeout=timeout
        )

    def expect_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expects the card to have a specific height.

        Parameters
        ----------
        value
            The expected height value.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_style_to_have_value(
            self.loc_container, "height", value, timeout=timeout
        )
