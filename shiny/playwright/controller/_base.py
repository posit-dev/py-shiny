"""Facade classes for working with Shiny inputs/outputs in Playwright"""

# TODO-barret; Possibly move all navset's loc_containers to the parent element (e.g. NavsetCardUnderline should have the container be the containing card.) The `.loc` will then point to the `ul` that has the id
# TODO-barret; This should be the container and the `ul#{id}.navbar-nav` should be the loc
# TODO-barret; Maybe add a `loc_nav_item` that contains `> li.nav-item`?
# TODO-barret; Note: We have access to the panel via `.nav_panel("key")`
# TODO-barret; Maybe add `.loc_sidebar` for the sidebar?


from __future__ import annotations

import typing
from typing import Literal, Protocol

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

# Import `shiny`'s typing extentions.
# Since this is a private file, tell pyright to ignore the import
from ..._typing_extensions import TypeGuard
from ...types import MISSING_TYPE
from .._types import AttrValue, OptionalFloat, PatternOrStr, Timeout
from ..expect._internal import (
    expect_attribute_to_have_value as _expect_attribute_to_have_value,
)
from ..expect._internal import expect_style_to_have_value as _expect_style_to_have_value

"""
Questions:
* `_DateBase` is signaled as private, but `InputDateRange` will have two fields of `date_start` and `date_end`. Due to how the init selectors are created, they are not `InputDate` instances. Should we make `_DateBase` public?

* While `expect_*_to_have_value()` matches the setup of `expect(x).to_have_value()`, it is a bit verbose. Should we just use `expect_*()` as we only use it in a single context? (Only adding the suffix if other methods like `to_have_html()` or `to_have_text()` would make sense.)
    * Ans: Try things out
    * Ans 3-7-2023: Use small names as there is no need to differentiate using longer names.

* TODO-future; Make sure multiple usage of `timeout` has the proper values. Should followup usages be `0` to force it to be immediate? (Is `0` the right value?)
    * Ans: There was no definition of "now" for a timeout. 0 disables the timeout.
"""

"""
# Class definitions
* Fields
  * Try to mirror playwright as much as possible.
    * Do not use verbose methods as we do not need the long name of
      `expect_label_to_have_text()` as there is not `expect_label_to_have_html()`
      or `expect_label_to_have_attribute()` methods. Just use `expect_label()`
  * There are no properties, only methods; This allows for timeout values to be passed through and for complex methods.
    * Locators will stay as properties
  * Don't sub-class. For now, use `_` separatation and use `loc` or `value` as a prefix
* Approach
  * Use locators / playwright_expect as much as possible
    * It should not be necessary to use `assert` directly.
    * MUST wait for `Locator`s to do their job
  * DO NOT provide `value` methods
  * Add _set_ methods (or set like methods) only if a user would perform them
"""

"""
# Mixins
* Use mixins to add consistent functionality to different classes
* These classes should **never** be instantiated directly
* Use `typing.Protocol` to define the interface of what is required on `self`
* Add methods to the mixin if they are consistently used across multiple classes
  * If a method is only used in one class, it should be defined in that class
  * If a method is used inconsistently, make/use a helper method
"""

InitLocator = typing.Union[Locator, str]

R = typing.TypeVar("R")
M1 = typing.TypeVar("M1")
M2 = typing.TypeVar("M2")


def is_missing(x: object) -> TypeGuard[MISSING_TYPE]:
    return isinstance(x, MISSING_TYPE)


# TypeGuard does not work for `not isinstance(x, MISSING_TYPE)`
# See discussion for `StrictTypeGuard`: https://github.com/python/typing/discussions/1013
# Until then, we need `not_is_missing(x=)` to narrow within an `if` statement
def not_is_missing(x: R | MISSING_TYPE) -> TypeGuard[R]:
    return not isinstance(x, MISSING_TYPE)


def all_missing(*args: object) -> TypeGuard[MISSING_TYPE]:
    for arg in args:
        if not_is_missing(arg):
            return False
    return True


def maybe_missing(x: M1 | MISSING_TYPE, default: M2) -> M1 | M2:
    if isinstance(x, MISSING_TYPE):
        return default
    return x


def set_text(
    loc: Locator,
    text: str,
    *,
    delay: OptionalFloat = None,
    timeout: Timeout = None,
) -> None:
    """
    Sets the text of a DOM element.

    Parameters
    ----------
    loc
        Playwright `Locator` of the element.
    text
        The text to set.
    delay
        The delay between key presses in milliseconds. Defaults to `None`.
    timeout
        The maximum time to wait for the text to be set. Defaults to `None`.
    """
    # TODO-future; Composable set() method
    loc.fill("", timeout=timeout)  # Reset the value
    loc.type(text, delay=delay, timeout=timeout)  # Type the value


def _expect_multiple(loc: Locator, multiple: bool, timeout: Timeout = None) -> None:
    _expect_attribute_to_have_value(
        loc,
        "multiple",
        value="multiple" if multiple else None,
        timeout=timeout,
    )


######################################################
# # Inputs
######################################################


class UiBaseP(Protocol):
    id: str
    loc: Locator
    page: Page


class UiWithContainerP(UiBaseP, Protocol):
    """A protocol class representing UI with a container."""

    loc_container: Locator
    """
    Playwright `Locator` for the container of the UI element.
    """


class UiWithSidebarP(UiWithContainerP, Protocol):
    """A protocol class representing UI with an associated sidebar."""

    loc_sidebar: Locator
    """
    Playwright `Locator` for its sidebar of the UI element.
    """


class UiWithTitleP(UiWithContainerP, Protocol):
    """A protocol class representing UI with an associated title."""

    loc_title: Locator
    """
    Playwright `Locator` for its title of the UI element.
    """


class UiBase:
    """A base class representing shiny UI components."""

    # timeout: Timeout
    id: str
    """
    The browser DOM `id` of the UI element.
    """
    loc: Locator
    """
    Playwright `Locator` of the UI element.
    """
    page: Page
    """
    Playwright `Page` of the Shiny app.
    """

    def __init__(
        self,
        page: Page,
        *,
        id: str,
        loc: InitLocator,
    ) -> None:
        self.page = page
        # Needed?!? This is covered by `self.loc_root` and possibly `self.loc`
        self.id = id
        if isinstance(loc, str):
            loc = page.locator(loc)
        self.loc = loc

    @property
    # TODO; Can not publicly find `LocatorAssertions` in `playwright`
    def expect(self):
        """Expectation method equivalent to `playwright.expect(self.loc)`."""
        # TODO-karan-test: Search for `.loc)` and convert `expect(FOO.loc)` to `FOO.expect`. If we don't like the helper API, we should remove it.
        return playwright_expect(self.loc)


class UiWithContainer(UiBase):
    """
    A mixin class representing UI with a container.
    """

    loc_container: Locator
    """
    Playwright `Locator` for the container of the UI element.
    """

    def __init__(
        self,
        page: Page,
        *,
        id: str,
        loc: InitLocator,
        loc_container: InitLocator = "div.shiny-input-container",
    ) -> None:
        """
        Initializes the input with a container.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The id of the UI element.
        loc
            Playwright `Locator` of the UI element.
        loc_container
            Playwright `Locator` of the container of the UI element.
        """
        loc_is_str = isinstance(loc, str)
        loc_container_is_str = isinstance(loc_container, str)

        if loc_is_str and loc_container_is_str:
            loc_container = page.locator(loc_container)
            if loc == "xpath=.":
                # If `loc` is self, then use `loc_container` as `loc`
                loc = loc_container

            else:
                loc_container = loc_container.locator(
                    # `page.locator(loc)` is executed from within `loc_container`
                    "xpath=.",
                    has=page.locator(loc),
                )

                loc = loc_container.locator(loc)
        elif not loc_is_str and not loc_container_is_str:
            ...  # Do nothing; Use values as is
        else:
            raise ValueError(
                "`loc` and `loc_container` must both be strings or both be Locators"
            )

        super().__init__(
            page,
            id=id,
            loc=loc,
        )
        self.loc_container = loc_container


class UiWithLabel(UiWithContainer):
    """A mixin class representing UI components with a label."""

    loc_label: Locator
    """
    Playwright `Locator` for the label of the UI element.
    """

    def __init__(
        self,
        page: Page,
        *,
        id: str,
        loc: InitLocator,
        loc_container: InitLocator = "div.shiny-input-container",
        loc_label: InitLocator | None = None,
    ) -> None:
        """
        Initializes the input with a label.

        Parameters
        ----------
        page
            The page where the input is located.
        id
            The id of the UI element.
        loc
            Playwright `Locator` of the UI element.
        loc_container
            Playwright `Locator` of the container of the UI element.
        loc_label
            Playwright `Locator` of the label of the UI element. Defaults to `None`.
        """
        super().__init__(
            page,
            id=id,
            loc_container=loc_container,
            loc=loc,
        )

        if loc_label is None:
            loc_label = f"label#{id}-label"
        if isinstance(loc_label, str):
            loc_label = self.loc_container.locator(loc_label)
        self.loc_label = loc_label

    def expect_label(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the label of the input to have a specific text.

        Parameters
        ----------
        value
            The expected text value of the label.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        playwright_expect(self.loc_label).to_have_text(value, timeout=timeout)


class WidthLocStlyeM:
    """
    A mixin class that provides methods to control the width of input action buttons and action links.

    """

    def expect_width(
        self: UiBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `width` attribute of a DOM element to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `width` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc, "width", value, timeout=timeout)


class WidthLocM:
    """
    A mixin class representing the `.loc`'s width.

    This class provides methods to expect the width attribute of a DOM element.
    """

    def expect_width(
        self: UiBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `width` attribute of a DOM element to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `width` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "width", value=value, timeout=timeout)


# # Currently not being used, hence commenting
# class WidthContainerM:
#     """
#     A mixin class representing the container's width.

#     This class provides methods to expect the width attribute of a DOM element's container.
#     """

#     def expect_width(
#         self: UiWithContainerP,
#         value: AttrValue,
#         *,
#         timeout: Timeout = None,
#     ) -> None:
#         """
#         Expect the `width` attribute of a input's container to have a specific value.

#         Parameters
#         ----------
#         value
#             The expected value of the `width` attribute.
#         timeout
#             The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
#         """
#         _expect_attribute_to_have_value(
#             self.loc_container, "width", value=value, timeout=timeout
#         )


class WidthContainerStyleM:
    """
    A mixin class that provides methods to control the width of input elements, such as checkboxes, sliders and radio buttons.
    """

    def expect_width(
        self: UiWithContainerP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the input element to have a specific width.

        Parameters
        ----------
        value
            The expected width.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc_container, "width", value, timeout=timeout)


class InputActionBase(UiBase):
    def expect_label(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the label of the input button to have a specific value.

        Parameters
        ----------
        value
            The expected value of the label.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """

        loc_label = self.loc.locator(".action-label")
        playwright_expect(loc_label).to_have_text(value, timeout=timeout)

    def expect_icon(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the icon of the input button to have a specific value.

        Parameters
        ----------
        value
            The expected value of the icon.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """

        loc_icon = self.loc.locator(".action-icon")
        playwright_expect(loc_icon).to_have_text(value, timeout=timeout)

    def click(self, *, timeout: Timeout = None, **kwargs: object) -> None:
        """
        Clicks the input action.

        Parameters
        ----------
        timeout
            The maximum time to wait for the input action to be clicked. Defaults to `None`.
        """
        self.loc.click(timeout=timeout, **kwargs)  # pyright: ignore[reportArgumentType]


Resize = Literal["none", "both", "horizontal", "vertical"]


# * click:
#     * input_checkbox_group
#     * input_radio_buttons


######################################################
# # Outputs
######################################################


class OutputBaseP(Protocol):
    id: str
    loc: Locator
    page: Page
