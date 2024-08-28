from __future__ import annotations

import re

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect
from typing_extensions import Literal

from .._types import PatternOrStr, Timeout
from ..expect._internal import expect_class_to_have_value as _expect_class_to_have_value
from ..expect._internal import expect_style_to_have_value as _expect_style_to_have_value
from ._base import (
    InitLocator,
    UiWithContainer,
    UiWithContainerP,
    UiWithSidebarP,
    UiWithTitleP,
)
from ._expect import expect_locator_values_in_list


class _ExpectNavsetSidebarM:
    def expect_sidebar(
        self: UiWithSidebarP,
        exists: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Assert whether or not the sidebar exists within the navset.

        Parameters
        ----------
        exists
            `True` if the sidebar exists within the navset.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_sidebar).to_have_count(int(exists), timeout=timeout)


class _ExpectNavsetTitleM:
    """A mixin class for Navset title controls"""

    def expect_title(
        self: UiWithTitleP,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the navset title to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_title).to_have_text(value, timeout=timeout)


class _ExpectNavsetPlacementM:
    def expect_placement(
        self: UiWithContainerP,
        location: Literal["above", "below"] = "above",
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the navset to have the specified placement.

        Parameters
        ----------
        location
            The expected placement location. Defaults to `'above'`.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        ex_class = "card-header" if location == "above" else "card-footer"
        playwright_expect(self.loc_container.locator("..")).to_have_class(
            ex_class, timeout=timeout
        )


class NavPanel(UiWithContainer):
    """Controller for :func:`shiny.ui.nav_panel`."""

    """
    Playwright `Locator` for the content of the nav panel.
    """
    loc: Locator
    """
    Playwright `Locator` for the nav panel.
    """
    loc_container: Locator
    """
    Playwright `Locator` for the nav panel container.
    """
    panel_value: str
    """
    The `data-value` attribute used to identify the nav panel within the larger navset.
    """

    def __init__(self, page: Page, id: str, panel_value: str) -> None:
        """
        Initializes a new instance of the `NavPanel` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the nav panel.
        panel_value
            The panel value of the nav panel.
        """
        super().__init__(
            page,
            id=id,
            loc=f"a[role='tab'][data-value='{panel_value}']",
            loc_container=f"ul#{id}",
        )

        self.panel_value: str = panel_value

    # TODO-future: Make it a single locator expectation
    # get active content instead of assertion
    @property
    def loc_content(self) -> Locator:
        """
        Returns the locator for the content of the nav panel.

        Note: This requires 2 steps. Will not work if the overlay element is rapidly created during locator fetch
        """
        datatab_id = self.loc_container.get_attribute("data-tabsetid")
        return self.page.locator(
            f"div.tab-content[data-tabsetid='{datatab_id}'] > div.tab-pane[data-value='{self.panel_value}']"
        )

    def click(self, *, timeout: Timeout = None) -> None:
        """
        Clicks the nav panel.

        Parameters
        ----------
        timeout
            The maximum time to wait for the nav panel to be visible and interactable. Defaults to `None`.
        """
        self.loc.click(timeout=timeout)

    def expect_active(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expects the nav panel to be active or inactive.

        Parameters
        ----------
        value
            `True` if the nav panel is expected to be active, False otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc,
            "active",
            has_class=value,
            timeout=timeout,
        )

    def _expect_content_text(
        self, value: PatternOrStr, *, timeout: Timeout = None
    ) -> None:
        """
        Expects the nav panel content to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_content).to_have_text(value, timeout=timeout)


class _NavsetBase(UiWithContainer):
    """A Base mixin class for Nav controls"""

    def nav_panel(
        self,
        value: str,
    ) -> NavPanel:
        """
        Returns the nav panel (:class:`~shiny.playwright.controls.NavPanel`)
        with the specified value.

        Parameters
        ----------
        value
            The value of the nav panel.
        """
        return NavPanel(self.page, self.id, value)

    def set(self, value: str, *, timeout: Timeout = None) -> None:
        """
        Sets the state of the control to open or closed.

        Parameters
        ----------
        value
            The selected nav item.
        """
        self.nav_panel(value).click(timeout=timeout)

    def expect_value(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the control to have the specified value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        # data attribute of active tab and compare with value
        playwright_expect(
            self.loc_container.locator('a[role="tab"].active')
        ).to_have_attribute("data-value", value, timeout=timeout)

    # # TODO-future: Make it a single locator expectation
    # # get active content instead of assertion
    # @property
    # def loc_active_content(self) -> Locator:
    #     datatab_id = self.loc_container.get_attribute("data-tabsetid")
    #     return self.page.locator(
    #         f"div.tab-content[data-tabsetid='{datatab_id}'] > div.tab-pane.active"
    #     )

    def get_loc_active_content(self, *, timeout: Timeout = None) -> Locator:
        """
        Returns the locator for the active content.

        Parameters
        ----------
        timeout
            The maximum time to wait for the locator to appear. Defaults to `None`.
        """
        datatab_id = self.loc_container.get_attribute("data-tabsetid", timeout=timeout)
        return self.page.locator(
            f"div.tab-content[data-tabsetid='{datatab_id}'] > div.tab-pane.active"
        )

    def _expect_content_text(
        self, value: PatternOrStr, *, timeout: Timeout = None
    ) -> None:
        """
        Expects the control to have the specified content.

        Parameters
        ----------
        value
            The expected content.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.get_loc_active_content()).to_have_text(
            value, timeout=timeout
        )

    def expect_nav_values(
        self,
        value: list[PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the control to have the specified nav values.

        Parameters
        ----------
        value
            The expected nav values.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="a[role='tab']",
            arr_name="value",
            arr=value,
            key="data-value",
            timeout=timeout,
        )

    def expect_nav_titles(
        self,
        value: list[PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the control to have the specified nav titles.

        Parameters
        ----------
        value
            The expected nav titles.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        self.expect.to_have_text(value, timeout=timeout)

    # # 2024-08-23-barret:
    # # These two functions are not implemented due to the inability to create a locator
    # # as some of the text contents are not contained within a defined parent element.
    # # This makes querying the header only (or footer only) impossible. When they are
    # # used within `navset_card_*()`, the header or footer _could_ be given within a
    # # `core_ui.CardItem()`. This CardItem could contain a TagList, putting us back into
    # # the same situation. Therefore, no move is currently the safe move. If we want to
    # # expose anything, maybe we could expose the navset card body container, but there
    # # is no container for the non-card navsets. :-(
    # def expect_header():
    #     raise NotImplementedError("Not implemented yet")
    # def expect_footer():
    #     raise NotImplementedError("Not implemented yet")


class NavsetTab(_NavsetBase):
    """Controller for :func:`shiny.ui.navset_tab`."""

    loc: Locator
    """
    Playwright `Locator` for the nav set tab.
    """
    loc_container: Locator
    """
    Playwright `Locator` for the nav set tab container.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `NavsetTab` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the nav set tab.
        """
        super().__init__(
            page,
            id=id,
            loc_container=f"ul#{id}.nav-tabs",
            loc="a[role='tab']",
        )


class NavsetPill(_NavsetBase):
    """Controller for :func:`shiny.ui.navset_pill`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `NavsetPill` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the nav set pill.
        """
        super().__init__(
            page,
            id=id,
            loc_container=f"ul#{id}.nav-pills",
            loc="> li.nav-item",
        )


class NavsetUnderline(_NavsetBase):
    """Controller for :func:`shiny.ui.navset_underline`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `NavsetUnderline` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the nav set underline.
        """
        super().__init__(
            page,
            id=id,
            loc_container=f"ul#{id}.nav-underline",
            loc="> li.nav-item",
        )


class NavsetPillList(_NavsetBase):
    """Controller for :func:`shiny.ui.navset_pill_list`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `NavsetPillList` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the nav set pill list.
        """
        super().__init__(
            page,
            id=id,
            loc_container=f"ul#{id}.nav-stacked",
            loc="> li.nav-item",
        )

    def expect_well(self, has_well: bool, *, timeout: Timeout = None) -> None:
        """
        Expects the navset pill list to have a well.

        Parameters
        ----------
        has_well
            `True` if the navset pill list is expected to have a well, `False` otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if has_well:
            playwright_expect(self.loc_container.locator("..")).to_have_class("well")
        else:
            playwright_expect(self.loc_container.locator("..")).not_to_have_class(
                "well"
            )


class _NavsetCardBase(
    _ExpectNavsetSidebarM,
    _ExpectNavsetTitleM,
    _NavsetBase,
):
    def __init__(
        self,
        page: Page,
        *,
        id: str,
        loc: InitLocator,
        loc_container: InitLocator,
    ) -> None:
        """
        Shim class to add consistent `.loc_sidebar` definition
        """
        super().__init__(
            page,
            id=id,
            loc_container=loc_container,
            loc=loc,
        )
        self.loc_sidebar = self.loc_container.locator("..").locator(
            "+ .bslib-sidebar-layout"
        )
        self.loc_title = (
            self.loc_container.locator("..")
            .locator("> span")
            .locator("xpath=.", has=self.page.locator(f"+ ul#{self.id}"))
        )


class NavsetCardTab(_NavsetCardBase):
    """Controller for :func:`shiny.ui.navset_card_tab`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `NavsetCardTab` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the nav set card tab.
        """
        super().__init__(
            page,
            id=id,
            loc_container=f".bslib-card > div > ul#{id}.nav-tabs",
            loc="> li.nav-item",
        )


class NavsetCardPill(_ExpectNavsetPlacementM, _NavsetCardBase):
    """Controller for :func:`shiny.ui.navset_card_pill`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `NavsetCardPill` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the nav set card pill.
        """
        super().__init__(
            page,
            id=id,
            loc_container=f".bslib-card > div > ul#{id}.nav-pills",
            loc="> li.nav-item",
        )


class NavsetCardUnderline(_ExpectNavsetPlacementM, _NavsetCardBase):
    """Controller for :func:`shiny.ui.navset_card_underline`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `NavsetCardUnderline` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the nav set card underline.
        """
        super().__init__(
            page,
            id=id,
            loc_container=f".bslib-card > div > ul#{id}.nav-underline",
            loc="> li.nav-item",
        )


class NavsetHidden(_NavsetBase):
    """Controller for :func:`shiny.ui.navset_hidden`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `NavsetHidden` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the nav set hidden.
        """
        super().__init__(
            page,
            id=id,
            loc_container=f"ul#{id}.nav-hidden",
            loc="> li.nav-item",
        )


class NavsetBar(
    _ExpectNavsetSidebarM,
    _ExpectNavsetTitleM,
    _NavsetBase,
):
    """Controller for :func:`shiny.ui.navset_bar`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `NavsetBar` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the nav set bar.
        """
        super().__init__(
            page,
            id=id,
            loc_container=f"ul#{id}.navbar-nav",
            loc="> li.nav-item",
        )
        self._loc_navbar = self.loc_container.locator("..").locator("..").locator("..")

        # This location is different than the `_NavsetCardBase.loc_title`
        self.loc_title = (
            self.loc_container.locator("..").locator("..").locator("> .navbar-brand")
        )
        # This location is different than the `_NavsetCardBase.loc_sidebar`
        self.loc_sidebar = (
            self.loc_container.locator("..")
            .locator("..")
            .locator("..")
            .locator("+ div > .bslib-sidebar-layout")
        )

    def expect_position(
        self,
        position: Literal[
            "fixed-top", "fixed-bottom", "static-top", "sticky-top"
        ] = "static-top",
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the navset bar to have the specified position.

        Parameters
        ----------
        position
            The expected position. Defaults to `'static-top'`.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if position == "static-top":
            # static-top class is not provided by the code.
            # Therefore we must check that all other classes are **not** found
            playwright_expect(self._loc_navbar).not_to_have_class(
                re.compile(r"(^|\s+)(fixed-top|fixed-bottom|sticky-top)(\s+|$)"),
                timeout=timeout,
            )
        else:
            playwright_expect(self._loc_navbar).to_have_class(
                re.compile(rf"{position}"), timeout=timeout
            )

    def expect_inverse(self, *, timeout: Timeout = None) -> None:
        """
        Expects the navset bar to be light text color if inverse is True

        Parameters
        ----------
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self._loc_navbar).to_have_class(
            re.compile("navbar-inverse"), timeout=timeout
        )

    def expect_bg(self, bg: str, *, timeout: Timeout = None) -> None:
        """
        Expects the navset bar to have the specified background color.

        Parameters
        ----------
        bg
            The expected background color.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_style_to_have_value(
            self._loc_navbar, "background-color", f"{bg} !important", timeout=timeout
        )

    def expect_gap(self, gap: str, *, timeout: Timeout = None) -> None:
        """
        Expects the navset bar to have the specified gap.

        Parameters
        ----------
        gap
            The expected gap.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_style_to_have_value(
            self.get_loc_active_content(), "gap", gap, timeout=timeout
        )

    def expect_layout(
        self, layout: Literal["fluid", "fixed"] = "fluid", *, timeout: Timeout = None
    ) -> None:
        """
        Expects the navset bar to have the specified layout.

        Parameters
        ----------
        layout
            The expected layout.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if layout == "fluid":
            playwright_expect(
                self.loc_container.locator("..").locator("..")
            ).to_have_class(re.compile("container-fluid"), timeout=timeout)
        else:
            playwright_expect(self.loc_container.locator("..")).to_have_class(
                re.compile("container"), timeout=timeout
            )
