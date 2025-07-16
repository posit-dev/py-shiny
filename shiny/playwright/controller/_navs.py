from __future__ import annotations

import re

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect
from typing_extensions import Literal

from ...types import ListOrTuple
from .._types import PatternOrStr, Timeout
from ..expect import expect_to_have_class, expect_to_have_style
from ..expect._internal import expect_attribute_to_have_value
from ..expect._internal import expect_class_to_have_value as _expect_class_to_have_value
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
        expect_to_have_class(
            self.loc_container.locator(".."), ex_class, timeout=timeout
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
    """A Base class for Nav controls"""

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

    def expect_well(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expects the navset pill list to have a well.

        Parameters
        ----------
        value
            `True` if the navset pill list is expected to be constructed with a well,
            `False` otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc_container.locator(".."), "well", has_class=value, timeout=timeout
        )

    def expect_widths(
        self, value: ListOrTuple[int], *, timeout: Timeout = None
    ) -> None:
        """
        Expects the navset pill list to have the specified widths.

        Parameters
        ----------
        value
            The expected widths of the navset pill list.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        widths = tuple(value)
        assert len(widths) == 2, "`value=` must be a tuple of two integers"
        assert all(
            isinstance(width, int) for width in widths
        ), "`value=` must be integers"

        loc_row_container = self.loc_container.locator("..").locator("..")

        # Make sure the two children are present
        loc_complicated = loc_row_container.locator(
            "xpath=.",
            has=self.page.locator(f"> div.col-sm-{widths[0]} + div.col-sm-{widths[1]}"),
        )

        # Make sure there are only two children present
        try:
            playwright_expect(loc_complicated.locator("> div")).to_have_count(
                2, timeout=timeout
            )
        except AssertionError as e:
            # Make sure there are only two children
            playwright_expect(loc_row_container.locator("> div")).to_have_count(
                2, timeout=1
            )

            expect_to_have_class(
                loc_row_container.locator("> div").first,
                f"col-sm-{widths[0]}",
                timeout=1,
            )
            expect_to_have_class(
                loc_row_container.locator("> div").last,
                f"col-sm-{widths[1]}",
                timeout=1,
            )

            # Re-raise the original exception if nothing could be debugged
            raise e


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


class _NavsetBarBase(
    _ExpectNavsetSidebarM,
    _ExpectNavsetTitleM,
    _NavsetBase,
):
    """Mixin class for common expectations of nav bars."""

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
            expect_to_have_class(self._loc_navbar, position, timeout=timeout)

    def expect_inverse(
        self,
        value: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the navset bar to be light text color if inverse is True

        Parameters
        ----------
        value
            `True` if the navset bar is expected to have inverse text color, `False` otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self._loc_navbar,
            "navbar-inverse",
            has_class=value,
            timeout=timeout,
        )

    def expect_bg(self, bg: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the navset bar to have the specified background color.

        Parameters
        ----------
        bg
            The expected background color.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        expect_to_have_style(
            self._loc_navbar,
            "background-color",
            f"{bg} !important",
            timeout=timeout,
        )

    def expect_gap(self, gap: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the navset bar to have the specified gap.

        Parameters
        ----------
        gap
            The expected gap.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        expect_to_have_style(
            self.get_loc_active_content(),
            "gap",
            gap,
            timeout=timeout,
        )

    def expect_fluid(
        self,
        value: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the navset bar to have a fluid or fixed layout.

        Parameters
        ----------
        value
            `True` if the layout is `fluid` or `False` if it is `fixed`.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if value:
            expect_to_have_class(
                self._loc_navbar.locator("> div"),
                "container-fluid",
                timeout=timeout,
            )
        else:
            expect_to_have_class(
                self._loc_navbar.locator("> div"),
                "container",
                timeout=timeout,
            )


class NavsetBar(_NavsetBarBase):
    """Controller for :func:`shiny.ui.navset_bar`."""


class PageNavbar(_NavsetBarBase):
    """Controller for :func:`shiny.ui.page_navbar`."""

    def expect_fillable(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expects the main content area to be considered a fillable (i.e., flexbox) container

        Parameters
        ----------
        value
            `True` if the main content area is expected to be fillable, `False` otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        # confirm page is fillable
        _expect_class_to_have_value(
            self.page.locator("body"),
            "bslib-page-fill",
            has_class=value,
            timeout=timeout,
        )

        # confirm content is fillable
        _expect_class_to_have_value(
            self.get_loc_active_content(),
            "html-fill-container",
            has_class=value,
            timeout=timeout,
        )

    def expect_fillable_mobile(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expects the main content area to be considered a fillable (i.e., flexbox) container on mobile
        This method will always call `.expect_fillable(True)` first to ensure the fillable property is set

        Parameters
        ----------
        value
            `True` if the main content area is expected to be fillable on mobile, `False` otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """

        # This is important since fillable_mobile needs fillable property to be True
        self.expect_fillable(True, timeout=timeout)
        _expect_class_to_have_value(
            self.page.locator("body"),
            "bslib-flow-mobile",
            has_class=not value,
            timeout=timeout,
        )

    def expect_window_title(
        self, title: PatternOrStr, *, timeout: Timeout = None
    ) -> None:
        """
        Expects the window title to have the specified text.

        Parameters
        ----------
        title
            The expected window title.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.page).to_have_title(title, timeout=timeout)

    def expect_lang(self, lang: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the HTML tag to have the specified language.

        Parameters
        ----------
        lang
            The expected language.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        expect_attribute_to_have_value(
            self.page.locator("html"),
            "lang",
            lang,
            timeout=timeout,
        )
