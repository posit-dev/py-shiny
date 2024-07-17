"""Facade classes for working with Shiny inputs/outputs in Playwright"""

from __future__ import annotations

import json
import pathlib
import platform
import re
import time
import typing
from typing import Literal, Optional, Protocol

from playwright.sync_api import FilePayload, FloatRect, Locator, Page, Position
from playwright.sync_api import expect as playwright_expect

from shiny.render._data_frame import ColumnFilter, ColumnSort

# Import `shiny`'s typing extentions.
# Since this is a private file, tell pyright to ignore the import
from ..._typing_extensions import TypeGuard
from ...types import MISSING, MISSING_TYPE, ListOrTuple
from .._types import (
    AttrValue,
    ListPatternOrStr,
    OptionalFloat,
    PatternOrStr,
    StyleValue,
    Timeout,
)
from ..expect import expect_not_to_have_class, expect_to_have_class
from ..expect._expect import _attr_match_str, _xpath_match_str
from ..expect._internal import (
    expect_attribute_to_have_value as _expect_attribute_to_have_value,
)
from ..expect._internal import expect_class_to_have_value as _expect_class_to_have_value
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
    value = "True" if multiple else None
    _expect_style_to_have_value(loc, "multiple", value, timeout=timeout)


######################################################
# # Inputs
######################################################


class _UiBaseP(Protocol):
    id: str
    loc: Locator
    page: Page


class _UiWithContainerP(_UiBaseP, Protocol):
    """A protocol class representing UI with a container."""

    loc_container: Locator
    """
    Playwright `Locator` for the container of the UI element.
    """


class _UiBase:
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


class _UiWithContainer(_UiBase):
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
                loc_container = loc_container.filter(
                    # `page.locator(loc)` is executed from within `loc_container`
                    has=page.locator(loc)
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


class _UiWithLabel(_UiWithContainer):
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


class _WidthLocM:
    """
    A mixin class representing the `.loc`'s width.

    This class provides methods to expect the width attribute of a DOM element.
    """

    def expect_width(
        self: _UiBaseP,
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


class _WidthContainerM:
    """
    A mixin class representing the container's width.

    This class provides methods to expect the width attribute of a DOM element's container.
    """

    def expect_width(
        self: _UiWithContainerP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `width` attribute of a input's container to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `width` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc_container, "width", value=value, timeout=timeout
        )


class _SetTextM:
    def set(self: _UiBaseP, value: str, *, timeout: Timeout = None) -> None:
        """
        Sets the text value

        Parameters
        ----------
        value
            The text to set.
        timeout
            The maximum time to wait for the text to be set. Defaults to `None`.
        """
        set_text(self.loc, value, timeout=timeout)


class _ExpectTextInputValueM:
    """A mixin class for text input values."""

    def expect_value(
        self: _UiBaseP,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the value of the text input to have a specific value.

        Parameters
        ----------
        value
            The expected value of the text input.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        playwright_expect(self.loc).to_have_value(value, timeout=timeout)


class InputNumeric(
    _SetTextM,
    _ExpectTextInputValueM,
    _WidthLocM,
    _UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_numeric`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes the input numeric Playwright control.

        Parameters
        ----------
        page
            The page where the input numeric is located.
        id
            The id of the input numeric.
        """
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}[type=number].shiny-bound-input",
        )

    def expect_min(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the minimum numeric value to be a specific value.

        Parameters
        ----------
        value
            The expected minimum numeric value.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "min", value=value, timeout=timeout)

    def expect_max(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the maximum numeric value to be a specific value.

        Parameters
        ----------
        value
            The expected maximum numeric value.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "max", value=value, timeout=timeout)

    def expect_step(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect step value when incrementing/decrementing the numeric input.

        Parameters
        ----------
        value
            The expected step value for the numeric input.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "step", value=value, timeout=timeout)


class _ExpectSpellcheckAttrM:
    """
    A mixin class for the spellcheck attribute.
    """

    def expect_spellcheck(
        self: _UiBaseP,
        value: Literal["true", "false"] | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `spellcheck` attribute of the input to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `spellcheck` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        # self.spellcheck.expect_to_have_value(value, timeout=timeout)
        _expect_attribute_to_have_value(
            self.loc, "spellcheck", value=value, timeout=timeout
        )


class _ExpectPlaceholderAttrM:
    def expect_placeholder(
        self: _UiBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `placeholder` attribute of the input to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `placeholder` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "placeholder", value=value, timeout=timeout
        )


class _ExpectAutocompleteAttrM:
    def expect_autocomplete(
        self: _UiBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `autocomplete` attribute of the input to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `autocomplete` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "autocomplete", value=value, timeout=timeout
        )


class InputText(
    _SetTextM,
    _ExpectTextInputValueM,
    _WidthLocM,
    _ExpectPlaceholderAttrM,
    _ExpectAutocompleteAttrM,
    _ExpectSpellcheckAttrM,
    _UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_text`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes the input text.

        Parameters
        ----------
        page
            The page where the input text is located.
        id
            The id of the input text.
        """
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}[type=text].shiny-bound-input",
        )


class InputPassword(
    _SetTextM,
    _ExpectTextInputValueM,
    _ExpectPlaceholderAttrM,
    _UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_password`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes the input password.

        Parameters
        ----------
        page
            The page where the input password is located.
        id
            The id of the input password.
        """
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}[type=password].shiny-bound-input",
        )

    # This class does not inherit from `_WidthContainerM`
    # as the width is in the element style
    def expect_width(
        self,
        value: StyleValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `width` attribute of the input password to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `width` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc_container, "width", value, timeout=timeout)


Resize = Literal["none", "both", "horizontal", "vertical"]


class InputTextArea(
    _SetTextM,
    _ExpectTextInputValueM,
    _ExpectPlaceholderAttrM,
    _ExpectAutocompleteAttrM,
    _ExpectSpellcheckAttrM,
    _UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_text_area`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes the input text area.

        Parameters
        ----------
        page
            The page where the input text area is located.
        id
            The id of the input text area.
        """
        super().__init__(
            page,
            id=id,
            loc=f"textarea#{id}.shiny-bound-input",
        )

    def expect_width(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expect the `width` attribute of the input text area to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `width` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        if value is None:
            _expect_style_to_have_value(
                self.loc_container,
                "width",
                None,
                timeout=timeout,
            )
            _expect_style_to_have_value(self.loc, "width", "100%", timeout=timeout)
        else:
            _expect_style_to_have_value(
                self.loc_container, "width", value, timeout=timeout
            )
            _expect_style_to_have_value(self.loc, "width", None, timeout=timeout)

    def expect_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expect the `height` attribute of the input text area to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `height` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc, "height", value, timeout=timeout)

    def expect_cols(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the `cols` attribute of the input text area to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `cols` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "cols", value=value, timeout=timeout)

    def expect_rows(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the `rows` attribute of the input text area to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `rows` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "rows", value=value, timeout=timeout)

    def expect_resize(
        self,
        value: Resize | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `resize` attribute of the input text area to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `resize` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "resize", value=value, timeout=timeout
        )

    def expect_autoresize(
        self,
        value: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `autoresize` attribute of the input text area to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `autoresize` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc,
            "textarea-autoresize",
            has_class=value,
            timeout=timeout,
        )


class _InputSelectBase(
    _WidthLocM,
    _UiWithLabel,
):
    loc_selected: Locator
    """
    Playwright `Locator` for the selected option of the input select.
    """
    loc_choices: Locator
    """
    Playwright `Locator` for the choices of the input select.
    """
    loc_choice_groups: Locator
    """
    Playwright `Locator` for the choice groups of the input select.
    """

    def __init__(
        self,
        page: Page,
        id: str,
        *,
        select_class: str = "",
    ) -> None:
        """
        Initializes the input select.

        Parameters
        ----------
        page
            The page where the input select is located.
        id
            The id of the input select.
        select_class
            The class of the select element. Defaults to "".
        """
        super().__init__(
            page,
            id=id,
            loc=f"select#{id}.shiny-bound-input{select_class}",
        )
        self.loc_selected = self.loc.locator("option:checked")
        self.loc_choices = self.loc.locator("option")
        self.loc_choice_groups = self.loc.locator("optgroup")

    def set(
        self,
        selected: str | ListOrTuple[str],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Sets the selected option(s) of the input select.

        Parameters
        ----------
        selected
            The value(s) of the selected option(s).
        timeout
            The maximum time to wait for the selection to be set. Defaults to `None`.
        """
        if isinstance(selected, str):
            selected = [selected]
        self.loc.select_option(value=selected, timeout=timeout)

    def expect_choices(
        self,
        # TODO-future; support patterns?
        choices: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the available options of the input select to be an exact match.

        Parameters
        ----------
        choices
            The expected choices of the input select.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """

        # Playwright doesn't like lists of size 0. Instead, check for empty locator
        if len(choices) == 0:
            playwright_expect(self.loc_choices).to_have_count(0, timeout=timeout)
            return

        _MultipleDomItems.expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="option",
            arr_name="choices",
            arr=choices,
            timeout=timeout,
        )

    def expect_selected(
        self,
        value: PatternOrStr | ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the selected option(s) of the input select to be an exact match.

        Parameters
        ----------
        value
            The expected value(s) of the selected option(s).
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        # Playwright doesn't like lists of size 0
        if isinstance(value, list) and len(value) == 0:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        if isinstance(value, list):
            self.expect.to_have_values(value, timeout=timeout)
        else:
            self.expect.to_have_value(value, timeout=timeout)

        # _MultipleDomItems.expect_locator_values_in_list(
        #     page=self.page,
        #     loc_container=self.loc_container,
        #     el_type="option",
        #     arr_name="selected",
        #     arr=selected,
        #     timeout=timeout,
        #     is_checked=True,
        # )

    def expect_choice_groups(
        self,
        # TODO-future; support patterns?
        choice_groups: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the choice groups of the input select to be an exact match.

        Parameters
        ----------
        choice_groups
            The expected choice groups of the input select.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """

        # Playwright doesn't like lists of size 0. Instead, use `None`
        if len(choice_groups) == 0:
            playwright_expect(self.loc_choice_groups).to_have_count(0, timeout=timeout)
            return

        _MultipleDomItems.expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="optgroup",
            arr_name="choice_groups",
            arr=choice_groups,
            timeout=timeout,
            key="label",
        )

    def expect_choice_labels(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the choice labels of the input select to be an exact match.

        Parameters
        ----------
        value
            The expected choice labels of the input select.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if len(value) == 0:
            playwright_expect(self.loc_choices).to_have_count(0, timeout=timeout)
            return
        playwright_expect(self.loc_choices).to_have_text(value, timeout=timeout)

    # multiple: bool = False,
    def expect_multiple(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the input select to allow multiple selections.

        Parameters
        ----------
        value
            Whether the input select allows multiple selections.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_multiple(self.loc, value, timeout=timeout)

    def expect_size(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the size attribute of the input select to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `size` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc,
            "size",
            value=value,
            timeout=timeout,
        )


class InputSelect(_InputSelectBase):
    """Controller for :func:`shiny.ui.input_select`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes the input select.

        Parameters
        ----------
        page
            The page where the input select is located.
        id
            The id of the input select.
        """
        super().__init__(
            page,
            id=id,
            select_class=".form-select",
        )

    # selectize: bool = False,
    def expect_selectize(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the input select to be selectize.

        Parameters
        ----------
        value
            Whether the input select is selectize.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        # class_=None if selectize else "form-select",
        _expect_class_to_have_value(
            self.loc,
            "form-select",
            has_class=not value,
            timeout=timeout,
        )


class InputSelectize(
    _UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_selectize`."""

    def __init__(self, page: Page, id: str) -> None:
        super().__init__(page, id=id, loc=f"#{id} + .selectize-control")
        self._loc_dropdown = self.loc.locator("> .selectize-dropdown")
        self._loc_events = self.loc.locator("> .selectize-input")
        self._loc_selectize = self._loc_dropdown.locator(
            "> .selectize-dropdown-content"
        )
        self.loc = self.loc_container.locator(f"select#{id}")
        self.loc_choice_groups = self._loc_selectize.locator(
            "> .optgroup > .optgroup-header"
        )
        # Do not use `.option` class as we are not guaranteed to have it.
        # We are only guaranteed to have `data-value` attribute for each _option_
        self.loc_choices = self._loc_selectize.locator("[data-value]")
        self.loc_selected = self.loc_container.locator(f"select#{id} > option")

    def set(
        self,
        selected: str | list[str],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Sets the selected option(s) of the input selectize.

        Parameters
        ----------
        selected
            The value(s) of the selected option(s).
        timeout
            The maximum time to wait for the selection to be set. Defaults to `None`.
        """
        if isinstance(selected, str):
            selected = [selected]
        self._loc_events.click()
        for value in selected:
            self._loc_selectize.locator(f"[data-value='{value}']").click(
                timeout=timeout
            )
        self._loc_events.press("Escape")

    def expect_choices(
        self,
        # TODO-future; support patterns?
        choices: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the available options of the input selectize to be an exact match.

        Parameters
        ----------
        choices
            The expected choices of the input select.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        self._populate_dom()
        # Playwright doesn't like lists of size 0. Instead, check for empty locator
        if len(choices) == 0:
            playwright_expect(self.loc_choices).to_have_count(0, timeout=timeout)
            return

        _MultipleDomItems.expect_locator_values_in_list(
            page=self.page,
            loc_container=self._loc_selectize,
            el_type=self.page.locator("[data-value]"),
            arr_name="choices",
            arr=choices,
            key="data-value",
            timeout=timeout,
        )

    def expect_selected(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the selected option(s) of the input select to be an exact match.

        Parameters
        ----------
        value
            The expected value(s) of the selected option(s).
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        # Playwright doesn't like lists of size 0
        if isinstance(value, list) and len(value) == 0:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        _MultipleDomItems.expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc,
            el_type=self.page.locator("> option"),
            arr_name="value",
            arr=value,
            key="value",
        )

    def _populate_dom(self, timeout: Timeout = None) -> None:
        """
        The click and Escape keypress is used to load the DOM elements
        """
        self._loc_events.click(timeout=timeout)
        _expect_style_to_have_value(
            self._loc_dropdown, "display", "block", timeout=timeout
        )
        self.page.locator("body").click(timeout=timeout)
        _expect_style_to_have_value(
            self._loc_dropdown, "display", "none", timeout=timeout
        )

    def expect_choice_groups(
        self,
        choice_groups: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the choice groups of the input select to be an exact match.

        Parameters
        ----------
        choice_groups
            The expected choice groups of the input select.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        self._populate_dom()
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if len(choice_groups) == 0:
            playwright_expect(self.loc_choice_groups).to_have_count(0, timeout=timeout)
            return

        playwright_expect(self.loc_choice_groups).to_have_text(
            choice_groups, timeout=timeout
        )

    def expect_choice_labels(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the choice labels of the input selectize to be an exact match.

        Parameters
        ----------
        value
            The expected choice labels of the input select.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        self._populate_dom()
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if len(value) == 0:
            playwright_expect(self.loc_choices).to_have_count(0, timeout=timeout)
            return
        playwright_expect(self.loc_choices).to_have_text(value, timeout=timeout)

    # multiple: bool = False,
    def expect_multiple(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the input selectize to allow multiple selections.

        Parameters
        ----------
        value
            Whether the input select allows multiple selections.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        if value:
            _expect_attribute_to_have_value(
                self.loc, "multiple", "multiple", timeout=timeout
            )
        else:
            _expect_attribute_to_have_value(self.loc, "multiple", None, timeout=timeout)


class _InputActionBase(_UiBase):
    def expect_label(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the label of the input button to have a specific value.

        Note: This must include the icon if it is present!

        Parameters
        ----------
        value
            The expected value of the label.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """

        self.expect.to_have_text(value, timeout=timeout)

    def click(self, *, timeout: Timeout = None, **kwargs: object) -> None:
        """
        Clicks the input action.

        Parameters
        ----------
        timeout
            The maximum time to wait for the input action to be clicked. Defaults to `None`.
        """
        self.loc.click(timeout=timeout, **kwargs)  # pyright: ignore[reportArgumentType]


class InputActionButton(
    _WidthLocM,
    _InputActionBase,
):
    """Controller for :func:`shiny.ui.input_action_button`."""

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initializes the input action button.

        Parameters
        ----------
        page
            The page where the input action button is located.
        id
            The id of the input action button.
        """
        super().__init__(
            page,
            id=id,
            loc=f"button#{id}.action-button.shiny-bound-input",
        )


class InputDarkMode(_UiBase):
    """Controller for :func:`shiny.ui.input_dark_mode`."""

    def __init__(
        self,
        page: Page,
        id: Optional[str] | None,
    ) -> None:
        """
        Initializes the input dark mode.

        Parameters
        ----------
        page
            The page where the input dark mode is located.
        id
            The id of the input dark mode.
        """
        id_selector = "" if id is None else f"#{id}"

        super().__init__(
            page,
            id="" if id is None else id,
            loc=f"bslib-input-dark-mode{id_selector}",
        )

    def click(self, *, timeout: Timeout = None):
        """
        Clicks the input dark mode.

        Parameters
        ----------
        timeout
            The maximum time to wait for the input dark mode to be clicked. Defaults to `None`.
        """
        self.loc.click(timeout=timeout)
        return self

    def expect_mode(self, value: str, *, timeout: Timeout = None):
        """
        Expect the `mode` attribute of the input dark mode to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `mode` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "mode", value=value, timeout=timeout)
        self.expect_page_mode(value, timeout=timeout)
        return self

    def expect_page_mode(self, value: str, *, timeout: Timeout = None):
        """
        Expect the page to have a specific dark mode value.

        Parameters
        ----------
        value
            The expected value of the page's dark mode.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.page.locator("html"), "data-bs-theme", value=value, timeout=timeout
        )
        return self

    def expect_attribute(self, value: str, *, timeout: Timeout = None):
        """
        Expect the attribute named `attribute` of the input dark mode to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `attribute` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "attribute", value=value, timeout=timeout
        )
        return self


class InputTaskButton(
    _WidthLocM,
    _InputActionBase,
):
    """Controller for :func:`shiny.ui.input_task_button`."""

    # TODO-Karan: Test auto_reset functionality
    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initializes the input task button.

        Parameters
        ----------
        page
            The page where the input task button is located.
        id
            The id of the input task button.
        """
        super().__init__(
            page,
            id=id,
            loc=f"button#{id}.bslib-task-button.shiny-bound-input",
        )

    def expect_state(
        self,
        value: Literal["ready", "busy"] | str,
        *,
        timeout: Timeout = None,
    ):
        """
        Expect the state of the input task button to have a specific value.

        Parameters
        ----------
        value
            The expected value of the state of the input task button.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc.locator("> bslib-switch-inline"),
            name="case",
            value=value,
            timeout=timeout,
        )

    def expect_label(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expect the label of the input task button to have a specific value.

        Parameters
        ----------
        value
            The expected value of the label.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        self.expect_label_ready(value, timeout=timeout)

    def expect_label_ready(self, value: PatternOrStr, *, timeout: Timeout = None):
        """
        Expect the label of a ready input task button to have a specific value.

        Parameters
        ----------
        value
            The expected value of the label.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        self.expect_label_state("ready", value, timeout=timeout)

    def expect_label_busy(self, value: PatternOrStr, *, timeout: Timeout = None):
        """
        Expect the label of a busy input task button to have a specific value.

        Parameters
        ----------
        value
            The expected value of the label.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        self.expect_label_state("busy", value, timeout=timeout)

    def expect_label_state(
        self,
        state: str,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ):
        """
        Expect the label of the input task button to have a specific value in a specific state.

        Parameters
        ----------
        state
            The state of the input task button.
        value
            The expected value of the label.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        playwright_expect(
            self.loc.locator(f"> bslib-switch-inline > span[slot='{state}']")
        ).to_have_text(value, timeout=timeout)

    def expect_auto_reset(self, value: bool, timeout: Timeout = None):
        """
        Expect the `auto-reset` attribute of the input task button to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `auto-reset` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc,
            name="data-auto-reset",
            value="" if value else None,
            timeout=timeout,
        )


class InputActionLink(_InputActionBase):
    """Controller for :func:`shiny.ui.input_action_link`."""

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initializes the input action link.

        Parameters
        ----------
        page
            The page where the input action link is located.
        id
            The id of the input action link.
        """
        super().__init__(
            page,
            id=id,
            loc=f"a#{id}.action-button.shiny-bound-input",
        )


# * click:
#     * input_checkbox_group
#     * input_radio_buttons


class _InputCheckboxBase(
    _WidthContainerM,
    _UiWithLabel,
):
    def __init__(
        self, page: Page, id: str, loc: InitLocator, loc_label: str | None
    ) -> None:
        """
        Initializes the input checkbox.

        Parameters
        ----------
        page
            The page where the input checkbox is located.
        id
            The id of the input checkbox.
        loc
            Playwright `Locator` of the input checkbox.
        loc_label
            Playwright `Locator` of the label of the input checkbox.
        """
        super().__init__(
            page,
            id=id,
            loc=loc,
            loc_label=loc_label,
        )

    def set(self, value: bool, *, timeout: Timeout = None, **kwargs: object) -> None:
        """
        Sets the input checkbox.

        Parameters
        ----------
        value
            The value of the input checkbox.
        timeout
            The maximum time to wait for the input checkbox to be set. Defaults to `None`.
        """
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        self.loc.set_checked(
            value, timeout=timeout, **kwargs  # pyright: ignore[reportArgumentType]
        )

    # TODO-karan-test: Convert usage of _toggle() to set()
    def _toggle(self, *, timeout: Timeout = None, **kwargs: object) -> None:
        """
        Toggles the input checkbox.

        Parameters
        ----------
        timeout
            The maximum time to wait for the input checkbox to be toggled. Defaults to `None`.
        """
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        self.loc.click(timeout=timeout, **kwargs)  # pyright: ignore[reportArgumentType]

    def expect_checked(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the input checkbox to be checked.

        Parameters
        ----------
        value
            Whether the input checkbox is checked.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        if value:
            self.expect.to_be_checked(timeout=timeout)
        else:
            self.expect.not_to_be_checked(timeout=timeout)


class InputCheckbox(_InputCheckboxBase):
    """Controller for :func:`shiny.ui.input_checkbox`."""

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initializes the input checkbox.

        Parameters
        ----------
        page
            The page where the input checkbox is located.
        id
            The id of the input checkbox.
        """
        super().__init__(
            page,
            id=id,
            loc=f"div.checkbox > label > input#{id}[type=checkbox].shiny-bound-input",
            loc_label="label > span",
        )


class InputSwitch(_InputCheckboxBase):
    """Controller for :func:`shiny.ui.input_switch`."""

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initializes the input switch.

        Parameters
        ----------
        page
            The page where the input switch is located.
        id
            The id of the input switch.
        """
        super().__init__(
            page,
            id=id,
            loc=f"div.form-switch > input#{id}[type=checkbox].shiny-bound-input",
            loc_label=f"label[for={id}]",
        )


# TODO-future: Move class methods to a separate module
class _MultipleDomItems:
    @staticmethod
    def assert_arr_is_unique(
        arr: ListPatternOrStr,
        msg: str,
    ) -> None:
        """
        Assert that the array is unique.

        Parameters
        ----------
        arr
            The array to check.
        msg
            The error message.
        """
        assert len(arr) == len(list(dict.fromkeys(arr))), msg

    @staticmethod
    def checked_css_str(
        is_checked: bool | MISSING_TYPE = MISSING,
    ) -> str:
        """
        Get the CSS string for checked elements.

        Parameters
        ----------
        is_checked
            Whether the elements are checked. Defaults to `MISSING`.
        """
        if is_missing(is_checked):
            return ""
        if is_checked:
            return ":checked"
        else:
            raise NotImplementedError("`is_checked = FALSE` is not verified yet")
            return ":not(:checked)"

    @staticmethod
    def expect_locator_contains_values_in_list(
        *,
        page: Page,
        loc_container: Locator,
        el_type: str,
        arr_name: str,
        arr: list[str],
        is_checked: bool | MISSING_TYPE = MISSING,
        timeout: Timeout = None,
        key: str = "value",
    ) -> None:
        """
        Expect the locator to contain the values in the list.

        The matching values must exist and be in order, but other values may also exist
        within the container.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        loc_container
            The container locator.
        el_type
            The element type.
        arr_name
            The variable name.
        arr
            The expected values.
        is_checked
            Whether the elements are checked. Defaults to `MISSING`.
        timeout
            The timeout for the expectation. Defaults to `None`.
        key
            The key. Defaults to `"value"`.
        """
        # Make sure the locator contains all of `arr`
        if not isinstance(arr, list):
            raise TypeError(f"`{arr_name}` must be a list")
        for item in arr:
            if not isinstance(item, str):
                raise TypeError(f"`{arr_name}` must be a list of strings")

        # Make sure the locator has len(uniq_arr) input elements
        _MultipleDomItems.assert_arr_is_unique(arr, f"`{arr_name}` must be unique")
        is_checked_str = _MultipleDomItems.checked_css_str(is_checked)

        # If there are no items, then the container needs to exist.
        # All containers contain 0 items.
        if len(arr) == 0:
            playwright_expect(loc_container).to_have_count(1, timeout=timeout)
            return

        loc_container_orig = loc_container

        # Find all items in set
        for item in arr:
            # Given the container, make sure it contains this locator
            loc_container = loc_container.locator(
                # Return self
                "xpath=.",
                # Simple approach as position is not needed
                has=page.locator(
                    f"{el_type}[{_attr_match_str(key, item)}]{is_checked_str}",
                ),
            )

        # If we are only looking to see if *some* (not *these only*) elements exist,
        # then we only need to check if the container locator (which must contain the elements) can be found
        try:
            playwright_expect(loc_container).to_have_count(1, timeout=timeout)
        except AssertionError as e:
            # Debug expections

            # Expecting container to exist (count = 1)
            playwright_expect(loc_container_orig).to_have_count(1, timeout=timeout)

            for item in arr:
                # Expecting item `{item}` to exist in container
                # Perform exact matches on strings.
                playwright_expect(
                    # Simple approach as position is not needed
                    loc_container_orig.locator(
                        f"{el_type}[{_attr_match_str(key, item)}]{is_checked_str}",
                    )
                ).to_have_count(1, timeout=timeout)

            # Could not find the reason why. Raising the original error.
            raise e

    @staticmethod
    def expect_locator_values_in_list(
        *,
        page: Page,
        loc_container: Locator,
        el_type: Locator | str,
        arr_name: str,
        arr: ListPatternOrStr,
        is_checked: bool | MISSING_TYPE = MISSING,
        timeout: Timeout = None,
        key: str = "value",
    ) -> None:
        """
        Expect the locator to contain the values in the list.

        The matching values must exist and be in order. No other matching values will be
        allowed within the container.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        loc_container
            The container locator.
        el_type
            The element type locator.
        arr_name
            The array name.
        arr
            The expected values.
        is_checked
            Whether the elements are checked. Defaults to `MISSING`.
        timeout
            The timeout for the expectation. Defaults to `None`.
        key
            The key. Defaults to `"value"`.
        """
        # Make sure the locator has exactly `arr` values

        # Make sure the locator has len(uniq_arr) input elements
        _MultipleDomItems.assert_arr_is_unique(arr, f"`{arr_name}` must be unique")

        if isinstance(el_type, Locator):
            if not isinstance(is_checked, MISSING_TYPE):
                raise RuntimeError(
                    "`is_checked` cannot be specified if `el_type` is a Locator"
                )
            loc_item = el_type
        else:
            is_checked_str = _MultipleDomItems.checked_css_str(is_checked)
            loc_item = page.locator(f"{el_type}{is_checked_str}")

        # If there are no items, then we should not have any elements
        if len(arr) == 0:
            playwright_expect(loc_container.locator(el_type)).to_have_count(
                0, timeout=timeout
            )
            return
        loc_container_orig = loc_container

        # Find all items in set
        for item, i in zip(arr, range(len(arr))):
            # Get all elements of type
            has_locator = loc_item
            # Get the `n`th matching element
            has_locator = has_locator.nth(i)
            # Make sure that element has the correct attribute value
            has_locator = has_locator.locator(
                f"xpath=self::*[{_xpath_match_str(key, item)}]"
            )

            # Given the container, make sure it contains this locator
            loc_container = loc_container.locator(
                # Return self
                "xpath=.",
                has=has_locator,
            )

        # Make sure other items are not in set
        # If we know all elements are contained in the container,
        # and all elements all unique, then it should have a count of `len(arr)`
        loc_inputs = loc_container.locator(loc_item)
        try:
            playwright_expect(loc_inputs).to_have_count(len(arr), timeout=timeout)
        except AssertionError as e:
            # Debug expections

            # Expecting container to exist (count = 1)
            playwright_expect(loc_container_orig).to_have_count(1, timeout=timeout)

            # Expecting the container to contain {len(arr)} items
            playwright_expect(loc_container_orig.locator(loc_item)).to_have_count(
                len(arr), timeout=timeout
            )

            for item, i in zip(arr, range(len(arr))):
                # Expecting item `{i}` to be `{item}`
                playwright_expect(
                    loc_container_orig.locator(loc_item).nth(i)
                ).to_have_attribute(key, item, timeout=timeout)

            # Could not find the reason why. Raising the original error.
            raise e


class _RadioButtonCheckboxGroupBase(_UiWithLabel):
    loc_choice_labels: Locator

    def expect_choice_labels(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the labels of the choices.

        Parameters
        ----------
        value
            The expected labels.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        if len(value) == 1:
            labels_val = value[0]
        else:
            labels_val = value
        playwright_expect(self.loc_choice_labels).to_have_text(
            labels_val,
            timeout=timeout,
        )

    def expect_inline(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the input to be inline.

        Parameters
        ----------
        value
            Whether the input is inline.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc_container,
            "shiny-input-container-inline",
            has_class=value,
            timeout=timeout,
        )


class InputCheckboxGroup(
    _WidthContainerM,
    _RadioButtonCheckboxGroupBase,
):
    """Controller for :func:`shiny.ui.input_checkbox_group`."""

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initialize the InputCheckboxGroup.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The id of the checkbox group.
        """
        super().__init__(
            page,
            id=id,
            # Similar to `select` tag in `InputSelect`'s `loc`
            # loc should be the `.shiny-bound-input` element
            # This happens to be the container
            loc="xpath=.",
            loc_container=f"div#{id}.shiny-input-checkboxgroup.shiny-bound-input",
        )

        # # Regular example
        #     <div class="shiny-options-group">
        #       <div class="checkbox">
        #         <label>
        #           <input type="checkbox" name="check1" value="red">
        #           <span><span style="color: #FF0000;">RED</span></span>
        # # Inline example
        #     <div class="shiny-options-group">
        #       <label class="checkbox-inline">
        #         <input type="checkbox" name="check2" value="magenta">
        #         <span><span style="color: #FF00AA;">MAGENTA</span></span>
        input_checkbox = f"> .shiny-options-group input[type=checkbox][name={id}]"
        self.loc_selected = self.loc.locator(f"{input_checkbox}:checked")
        self.loc_choices = self.loc.locator(f"{input_checkbox}")
        # Get sibling <span> containing the label text
        self.loc_choice_labels = self.loc.locator(f"{input_checkbox} + span")

    def set(
        self,
        # TODO-future: Allow `selected` to be a single Pattern to perform matching against many items
        selected: ListOrTuple[str],
        *,
        timeout: Timeout = None,
        **kwargs: object,
    ) -> None:
        """
        Set the selected checkboxes.

        Parameters
        ----------
        selected
            The values of the selected checkboxes.
        timeout
            The timeout for the action. Defaults to `None`.
        """
        # Having an arr of size 0 is allowed. Will uncheck everything
        if not isinstance(selected, list):
            raise TypeError("`selected` must be a list or tuple")
        for item in selected:
            if not isinstance(item, str):
                raise TypeError("`selected` must be a list of strings")

        # Make sure the selected items exist
        # Similar to `self.expect_choices(choices = selected)`, but with
        # `is_exact=False` to allow for values not in `selected`.
        _MultipleDomItems.expect_locator_contains_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="input[type=checkbox]",
            arr_name="selected",
            arr=selected,
            timeout=timeout,
        )

        def in_selected(value: str) -> bool:
            for item in selected:
                if isinstance(item, str):
                    if item == value:
                        return True
                elif isinstance(item, typing.Pattern):
                    if item.search(value):
                        return True
            return False

        # Could do with multiple locator calls,
        # but unchecking the elements that are not in `selected` is not possible
        # as `set_checked()` likes a single element.
        for checkbox in self.loc_choices.element_handles():
            is_selected = in_selected(checkbox.input_value(timeout=timeout))
            checkbox.set_checked(
                is_selected,
                timeout=timeout,
                **kwargs,  # pyright: ignore[reportArgumentType]
            )

    def expect_choices(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the checkbox choices.

        Parameters
        ----------
        value
            The expected choices.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _MultipleDomItems.expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="input[type=checkbox]",
            arr_name="choices",
            arr=value,
            timeout=timeout,
        )

    def expect_selected(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the selected checkboxes.

        Parameters
        ----------
        value
            The expected values of the selected checkboxes.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        # Playwright doesn't like lists of size 0
        if len(value) == 0:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        _MultipleDomItems.expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="input[type=checkbox]",
            arr_name="selected",
            arr=value,
            timeout=timeout,
            is_checked=True,
        )


class InputRadioButtons(
    _WidthContainerM,
    _RadioButtonCheckboxGroupBase,
):
    """Controller for :func:`shiny.ui.input_radio_buttons`."""

    loc_selected: Locator
    """
    Playwright `Locator` of the selected radio button.
    """
    loc_choices: Locator
    """
    Playwright `Locator` of the radio button choices.
    """
    loc_choice_labels: Locator
    """
    Playwright `Locator` of the labels of the radio button choices.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """Initialize the InputRadioButtons.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The id of the radio buttons.
        """
        super().__init__(
            page,
            id=id,
            # Similar to `select` tag in `InputSelect`'s `loc`
            # loc should be the `.shiny-bound-input` element
            # This happens to be the container
            loc="xpath=.",
            loc_container=f"div#{id}.shiny-input-radiogroup.shiny-bound-input",
        )

        # # Regular example
        #     <div class="shiny-options-group">
        #       <div class="radio">
        #         <label>
        #           <input type="radio" name="radio1" value="a" checked="checked">
        #           <span><span style="color:red;">A</span></span>
        # # Inline example
        #     <div class="shiny-options-group">
        #       <label class="radio-inline">
        #         <input type="radio" name="radio2" value="d" checked="checked">
        #         <span><span style="color:purple;">D</span></span>
        input_radio = f"> .shiny-options-group input[type=radio][name={id}]"
        self.loc_selected = self.loc.locator(f"{input_radio}:checked")
        self.loc_choices = self.loc.locator(f"{input_radio}")
        # Get sibling <span> containing the label text
        self.loc_choice_labels = self.loc.locator(f"{input_radio} + span")

    def set(
        self,
        selected: str,
        *,
        timeout: Timeout = None,
        **kwargs: object,
    ) -> None:
        """
        Set the selected radio button.

        Parameters
        ----------
        selected
            The value of the selected radio button.
        timeout
            The timeout for the action. Defaults to `None`.
        """
        if not isinstance(selected, str):
            raise TypeError("`selected` must be a string")

        # Only need to set.
        # The Browser will _unset_ the previously selected radio button
        self.loc_container.locator(
            f"label input[type=radio][{_attr_match_str('value', selected)}]"
        ).check(timeout=timeout)

    def expect_choices(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the radio button choices.

        Parameters
        ----------
        value
            The expected choices.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _MultipleDomItems.expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="input[type=radio]",
            arr_name="choices",
            arr=value,
            timeout=timeout,
        )

    def expect_selected(
        self,
        value: PatternOrStr | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the selected radio button.

        Parameters
        ----------
        value
            The expected value of the selected radio button.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if value is None:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        playwright_expect(self.loc_selected).to_have_value(value, timeout=timeout)


class InputFile(
    # _ExpectPlaceholderAttrM,
    _UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_file`."""

    loc_button: Locator
    """
    Playwright `Locator` of the button.
    """
    loc_file_display: Locator
    """
    Playwright `Locator` of the file display.
    """
    loc_progress: Locator
    """
    Playwright `Locator` of the progress bar.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initialize the InputFile.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The id of the file input.
        """
        super().__init__(
            page,
            id=id,
            loc=f"input[type=file]#{id}",
        )
        self.loc_button = self.loc_container.locator("label span.btn")
        self.loc_file_display = self.loc_container.locator("input[type=text]")
        self.loc_progress = self.loc_container.locator(".progress-bar")

    def set(
        self,
        file_path: (
            str
            | pathlib.Path
            | FilePayload
            | list[str | pathlib.Path]
            | list[FilePayload]
        ),
        *,
        timeout: Timeout = None,
        expect_complete_timeout: Timeout = 30 * 1000,
    ) -> None:
        """
        Set the file upload.

        Parameters
        ----------
        file_path
            The path to the file to upload.
        timeout
            The timeout for the action. Defaults to `None`.
        expect_complete_timeout
            The timeout for the expectation that the upload is complete. Defaults to `30 * 1000`.
        """
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        self.loc.set_input_files(file_path, timeout=timeout)
        if expect_complete_timeout is not None:
            self.expect_complete(timeout=expect_complete_timeout)

    # TODO-future: Let's make sure that if the upload errors out, expect_complete() fails.
    def expect_complete(
        self,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the file upload to be complete.

        Parameters
        ----------
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc_progress, "width", "100%", timeout=timeout)

    # TODO-future; Test multiple file upload
    def expect_multiple(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the `multiple` attribute to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `multiple` attribute.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_multiple(self.loc, value, timeout=timeout)

    def expect_accept(
        self,
        value: list[str] | AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `accept` attribute to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `accept` attribute.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        if isinstance(value, list):
            value = ",".join(value)
        _expect_attribute_to_have_value(self.loc, "accept", value, timeout=timeout)

    def expect_width(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expect the width of the input file to have a specific value.

        Parameters
        ----------
        value
            The expected value of the width.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc_container, "width", value, timeout=timeout)

    def expect_button_label(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the button label to have a specific value.

        Parameters
        ----------
        value
            The expected value of the button label.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        playwright_expect(self.loc_button).to_have_text(value, timeout=timeout)

    def expect_capture(
        self,
        value: Literal["environment", "user"] | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `capture` attribute to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `capture` attribute.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "capture", value, timeout=timeout)

    def expect_placeholder(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        _expect_attribute_to_have_value(
            self.loc_file_display, "placeholder", value=value, timeout=timeout
        )


class _InputSliderBase(_WidthLocM, _UiWithLabel):

    loc_irs: Locator
    """
    Playwright `Locator` of the input slider.
    """
    loc_irs_ticks: Locator
    """
    Playwright `Locator` of the input slider ticks.
    """
    loc_play_pause: Locator
    """
    Playwright `Locator` of the play/pause button.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initialize the InputSlider.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The id of the slider.
        """
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}",
        )
        self.loc_irs = self.loc_container.locator("> .irs.irs--shiny")
        self.loc_irs_ticks = self.loc_irs.locator("> .irs-grid > .irs-grid-text")
        self.loc_play_pause = self.loc_container.locator(
            "> .slider-animate-container a"
        )

    def expect_tick_labels(
        self,
        value: ListPatternOrStr | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the tick labels of the input slider.

        Parameters
        ----------
        value
            The expected tick labels.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        if value is None:
            playwright_expect(self.loc_irs_ticks).to_have_count(0)
            return

        playwright_expect(self.loc_irs_ticks).to_have_text(value, timeout=timeout)

    def expect_animate(self, exists: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the animate button to exist.

        Parameters
        ----------
        exists
            Whether the animate button should exist.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        animate_count = 1 if exists else 0
        playwright_expect(self.loc_play_pause).to_have_count(animate_count)

    # This method doesn't feel like it should accept text as the user does not control the value
    # They only control either `True` or `False`
    def expect_animate_options(
        self,
        *,
        loop: bool | MISSING_TYPE = MISSING,
        interval: float | MISSING_TYPE = MISSING,
        timeout: Timeout = None,
    ) -> None:
        if all_missing(loop, interval):
            raise ValueError("Must provide at least one of `loop` or `interval`")
        # TODO-future; Composable expectations
        self.expect_animate(exists=True, timeout=timeout)
        if not_is_missing(loop):
            _expect_attribute_to_have_value(
                self.loc_play_pause,
                "data-loop",
                "" if loop else None,
                timeout=timeout,
            )
        if not_is_missing(interval):
            _expect_attribute_to_have_value(
                self.loc_play_pause,
                "data-interval",
                str(interval),
                timeout=timeout,
            )

    # No `toggle` method as short animations with no loops can cause the button to
    # become `play` over and over again. Instead, have explicit `play` and `pause`
    # methods.
    def click_play(self, *, timeout: Timeout = None) -> None:
        """
        Click the play button.

        Parameters
        ----------
        timeout
            The timeout for the action. Defaults to `None`.
        """
        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)
        _expect_class_to_have_value(
            self.loc_play_pause,
            "playing",
            has_class=False,
            timeout=timeout,
        )
        self.loc_play_pause.click()

    def click_pause(self, *, timeout: Timeout = None) -> None:
        """
        Click the pause button.

        Parameters
        ----------
        timeout
            The timeout for the action. Defaults to `None`.
        """
        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)
        _expect_class_to_have_value(
            self.loc_play_pause, "playing", has_class=True, timeout=timeout
        )
        self.loc_play_pause.click()

    def expect_min(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `min` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-min", value=value, timeout=timeout
        )

    def expect_max(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `max` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-max", value=value, timeout=timeout
        )

    def expect_step(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `step` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-step", value=value, timeout=timeout
        )

    def expect_ticks(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `data-ticks` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-grid", value=value, timeout=timeout
        )

    def expect_sep(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `data-sep` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-prettify-separator", value=value, timeout=timeout
        )

    def expect_pre(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `data-pre` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-prefix", value=value, timeout=timeout
        )

    def expect_post(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `data-post` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-postfix", value=value, timeout=timeout
        )

    # def expect_data_type(
    #     self, value: AttrValue, *, timeout: Timeout = None
    # ) -> None:
    #     expect_attr(self.loc, "data-data-type", value=value, timeout=timeout)

    def expect_time_format(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Asserts that the input element has the expected `data-time-format` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-time-format", value=value, timeout=timeout
        )

    def expect_timezone(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Asserts that the input element has the expected `data-timezone` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-timezone", value=value, timeout=timeout
        )

    def expect_drag_range(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Asserts that the input element has the expected `data-drag-range` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-drag-interval", value=value, timeout=timeout
        )

    def _wait_for_container(self, *, timeout: Timeout = None) -> None:
        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)

    def _set_helper(
        self,
        *,
        value: str,
        irs_label: Locator,
        handle_center: Position,
        grid_bb: FloatRect,
        start_x: float,
        direction: Literal["left", "right"],
        max_err_values: int = 15,
    ) -> None:
        if direction == "left":
            pixel_increment = -1
            error_msg_direction = "right to left"
            min_pxls = -1 * (grid_bb["width"] + 1)

            def should_continue(cur_pxls: float) -> bool:
                return cur_pxls > min_pxls

        elif direction == "right":
            pixel_increment = 1
            error_msg_direction = "left to right"
            max_pxls = grid_bb["width"] + 1

            def should_continue(cur_pxls: float) -> bool:
                return cur_pxls <= max_pxls

        else:
            raise ValueError(f"Invalid direction: {direction}")

        # Move mouse to handle center and press down on mouse
        mouse = self.loc_container.page.mouse
        mouse.move(handle_center.get("x"), handle_center.get("y"))
        mouse.down()

        # Slow it down a bit. Like "type" for text, but to allow the slider label to catch up
        # This should be done for every `mouse.move()` call
        sleep_time = 0.05

        def slow_move(x: float, y: float, delay: float = sleep_time) -> None:
            """
            Slowly move the mouse to the given coordinates.

            Parameters
            ----------
            x
                The x-coordinate.
            y
                The y-coordinate.
            delay
                The delay between each move. Defaults to `sleep_time`.
            """
            mouse.move(x, y)
            time.sleep(delay)

        # Move all the way to the left
        handle_center_y = handle_center.get("y")
        slow_move(start_x, handle_center_y, delay=10 * sleep_time)

        # For each pixel in the grid width, check the text label
        pxls: int = 0
        found = False
        values_found: typing.Dict[str, bool] = {}
        cur_val = None
        while should_continue(pxls):
            # Get value
            cur_val = irs_label.inner_text()
            # Only store what could be used
            if len(values_found) <= max_err_values + 1:
                values_found[cur_val] = True

            # Quit if found
            if cur_val == value:
                found = True
                break

            # Not found; move handle to the right
            slow_move(start_x + pxls, handle_center_y)

            pxls += pixel_increment

        mouse.up()
        if not found:
            key_arr = list(values_found.keys())
            trail_txt = ""
            if len(key_arr) > max_err_values:
                key_arr = key_arr[:max_err_values]
                trail_txt = f", ...\nTo display more values, increase `set(max_err_values={max_err_values})`"
            values_found_txt = ", ".join([f'"{key}"' for key in key_arr])
            raise ValueError(
                f"Could not find value '{value}' when moving slider from {error_msg_direction}\n"
                + f"Values found:\n{values_found_txt}{trail_txt}"
            )

    def _grid_bb(self, *, timeout: Timeout = None) -> FloatRect:
        grid = self.loc_irs.locator("> .irs > .irs-line")
        grid_bb = grid.bounding_box(timeout=timeout)
        if grid_bb is None:
            raise RuntimeError("Couldn't find bounding box for .irs-line")
        return grid_bb

    def _handle_center(
        self,
        handle: Locator,
        *,
        name: str,
        timeout: Timeout = None,
    ) -> Position:
        handle_bb = handle.bounding_box(timeout=timeout)
        if handle_bb is None:
            raise RuntimeError(f"Couldn't find bounding box for {name}")

        handle_center: Position = {
            "x": handle_bb.get("x") + (handle_bb.get("width") / 2),
            "y": handle_bb.get("y") + (handle_bb.get("height") / 2),
        }
        return handle_center


class InputSlider(_InputSliderBase):
    """Controller for :func:`shiny.ui.input_slider`."""

    loc_irs_label: Locator
    """
    Playwright `Locator` of the input slider label.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initialize the InputSlider object.

        Parameters
        ----------
        page
            The Playwright Page object.
        id
            The id of the input element.
        """
        super().__init__(page, id=id)
        self.loc_irs_label = self.loc_irs.locator("> .irs > .irs-single")

    def expect_value(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Asserts that the input element has the expected value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_irs_label).to_have_text(value, timeout=timeout)

    def set(
        self,
        value: str,
        *,
        max_err_values: int = 15,
        timeout: Timeout = None,
    ) -> None:
        """
        Set the value of the slider.

        Parameters
        ----------
        value
            The value to set the slider to.
        max_err_values
            The maximum number of error values to display if the value is not found. Defaults to 15.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        self._wait_for_container(timeout=timeout)

        handle = self.loc_irs.locator("> .irs-handle")
        handle_center = self._handle_center(handle, name="handle", timeout=timeout)
        grid_bb = self._grid_bb(timeout=timeout)

        self._set_helper(
            value=value,
            irs_label=self.loc_irs_label,
            handle_center=handle_center,
            grid_bb=grid_bb,
            start_x=grid_bb["x"],
            direction="right",
            max_err_values=max_err_values,
        )


class InputSliderRange(_InputSliderBase):
    """Controller for :func:`shiny.ui.input_slider` with a slider range."""

    loc_irs_label_from: Locator
    """
    Playwright `Locator` of the input slider label for the `from` handle.
    """
    loc_irs_label_to: Locator
    """
    Playwright `Locator` of the input slider label for the `to` handle.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initialize the InputSliderRange object.

        Parameters
        ----------
        page
            The Playwright Page object.
        id
            The id of the input element.
        """
        super().__init__(page, id=id)
        self.loc_irs_label_from = self.loc_irs.locator("> .irs > .irs-from")
        self.loc_irs_label_to = self.loc_irs.locator("> .irs > .irs-to")

    def expect_value(
        self,
        value: (
            typing.Tuple[PatternOrStr, PatternOrStr]
            | typing.Tuple[PatternOrStr, MISSING_TYPE]
            | typing.Tuple[MISSING_TYPE, PatternOrStr]
        ),
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        if all_missing(*value):
            raise ValueError("Both `value` tuple entries cannot be `MISSING_TYPE`")
        from_val = value[0]
        to_val = value[1]

        # TODO-future; Composable expectations
        if not_is_missing(from_val):
            playwright_expect(self.loc_irs_label_from).to_have_text(
                from_val, timeout=timeout
            )
        if not_is_missing(to_val):
            playwright_expect(self.loc_irs_label_to).to_have_text(
                to_val, timeout=timeout
            )

    def _set_fraction(
        self,
        handle: Locator,
        fraction: float,
        *,
        name: str,
        timeout: Timeout = None,
    ) -> None:
        if fraction > 1 or fraction < 0:
            raise ValueError("`fraction` must be between 0 and 1")

        handle_center = self._handle_center(handle, name=name, timeout=timeout)
        grid_bb = self._grid_bb(timeout=timeout)
        mouse = self.loc_container.page.mouse
        mouse.move(x=handle_center.get("x"), y=handle_center.get("y"))
        mouse.down()
        mouse.move(
            grid_bb.get("x") + (fraction * grid_bb.get("width")),
            handle_center.get("y"),
        )
        mouse.up()

    def set(
        self,
        value: (
            typing.Tuple[str, str]
            | typing.Tuple[str, MISSING_TYPE]
            | typing.Tuple[MISSING_TYPE, str]
        ),
        *,
        max_err_values: int = 15,
        timeout: Timeout = None,
    ) -> None:
        """
        Set the value of the slider.

        Parameters
        ----------
        value
            The value to set the slider to.
        max_err_values
            The maximum number of error values to display if the value is not found. Defaults to 15.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        if all_missing(*value):
            raise ValueError("Both `value` tuple entries cannot be `MISSING_TYPE`")

        value_from = value[0]
        value_to = value[1]
        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)
        handle_from = self.loc_irs.locator("> .irs-handle.from")
        handle_to = self.loc_irs.locator("> .irs-handle.to")
        if not_is_missing(value_from):
            # Move `from` handle to the far left
            self._set_fraction(handle_from, 0, name="`from` handle", timeout=timeout)
        if not_is_missing(value_to):
            # Move `to` handle to the far right
            self._set_fraction(handle_to, 1, name="`to` handle", timeout=timeout)

        handle_center_from = self._handle_center(
            handle_from, name="`from` handle", timeout=timeout
        )
        grid_bb = self._grid_bb(timeout=timeout)

        # Handles are [possibly] now at their respective extreme value
        # Now let's move them towards the other end until we find the corresponding str

        if not_is_missing(value_from):
            self._set_helper(
                value=value_from,
                irs_label=self.loc_irs_label_from,
                handle_center=handle_center_from,
                grid_bb=grid_bb,
                # Start at the far left
                start_x=grid_bb["x"],
                # And move to the right
                direction="right",
                max_err_values=max_err_values,
            )

        handle_center_to = self._handle_center(
            handle_to, name="`to` handle", timeout=timeout
        )
        if not_is_missing(value_to):
            self._set_helper(
                value=value_to,
                irs_label=self.loc_irs_label_to,
                handle_center=handle_center_to,
                grid_bb=grid_bb,
                # Start at the far right
                start_x=grid_bb["x"] + grid_bb["width"],
                # And move to the left
                direction="left",
                max_err_values=max_err_values,
            )


class _DateBase(
    _SetTextM,
    _WidthContainerM,
    _UiWithLabel,
):

    # Due to the `language` parameter, we can't use `datetime.date` as a value type

    def expect_value(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        # if value is None:
        #     self.expect.to_be_empty(timeout=timeout)
        # else:
        self.expect.to_have_value(value, timeout=timeout)

    def expect_min_date(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-min-date` attribute value.

        Parameters
        ----------
        value
            The expected `data-min-date` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-min-date", value=value, timeout=timeout
        )

    def expect_max_date(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-max-date` attribute value.

        Parameters
        ----------
        value
            The expected `data-max-date` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-max-date", value=value, timeout=timeout
        )

    def expect_format(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-format` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-format` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-date-format", value=value, timeout=timeout
        )

    def expect_startview(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-start-view` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-start-view` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-date-start-view", value=value, timeout=timeout
        )

    def expect_weekstart(
        self,
        value: int | AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-week-start` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-week-start` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        if isinstance(value, int):
            value = str(value)
        _expect_attribute_to_have_value(
            self.loc, "data-date-week-start", value=value, timeout=timeout
        )

    def expect_language(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-language` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-language` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-date-language", value=value, timeout=timeout
        )

    # autoclose: bool = True,
    def expect_autoclose(
        self,
        value: Literal["true", "false"],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-autoclose` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-autoclose` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-date-autoclose", value=value, timeout=timeout
        )

    def expect_datesdisabled(
        self,
        value: list[str] | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-dates-disabled` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-dates-disabled` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        if isinstance(value, list):
            assert len(value) > 0, "`value` must be `None` or a non-empty list"
        value_str = "null" if value is None else json.dumps(value)
        _expect_attribute_to_have_value(
            self.loc,
            "data-date-dates-disabled",
            value=value_str,
            timeout=timeout,
        )

    def expect_daysofweekdisabled(
        self,
        value: list[int] | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-days-of-week-disabled` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-days-of-week-disabled` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        if isinstance(value, list):
            assert len(value) > 0, "`value` must be `None` or a non-empty list"
        value_str = "null" if value is None else json.dumps(value)
        _expect_attribute_to_have_value(
            self.loc,
            "data-date-days-of-week-disabled",
            value=value_str,
            timeout=timeout,
        )


class InputDate(_DateBase):
    def __init__(self, page: Page, id: str) -> None:
        """
        Initialize an InputDate object.

        Parameters
        ----------
        page
            The page object.
        id
            The id of the input element.
        """
        super().__init__(
            page,
            id=id,
            loc="input[type=text].form-control",
            loc_container=f"div#{id}.shiny-input-container",
        )


class InputDateRange(_WidthContainerM, _UiWithLabel):
    """Controller for :func:`shiny.ui.input_date_range`."""

    loc_separator: Locator
    """
    Playwright `Locator` of the separator between the two input elements.
    """
    loc_start: Locator
    """
    Playwright `Locator` of the start date input element.
    """
    loc_end: Locator
    """
    Playwright `Locator` of the end date input element.
    """
    date_start: _DateBase
    """
    The start date input element.
    """
    date_end: _DateBase
    """
    The end date input element.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initialize an InputDateRange object.

        Parameters
        ----------
        page
            The page object.
        id
            The id of the input element.
        """
        super().__init__(
            page,
            id=id,
            loc="input[type=text].form-control",
            loc_container=f"div#{id}.shiny-input-container",
        )
        self.loc_separator = self.loc_container.locator(".input-daterange > span")
        self.loc_start = self.loc.nth(0)
        self.loc_end = self.loc.nth(1)
        self.date_start = _DateBase(
            page,
            id=id,
            loc=self.loc_start,
            loc_label=self.loc_label,
            loc_container=self.loc_container,
        )
        self.date_end = _DateBase(
            page,
            id=id,
            loc=self.loc_end,
            loc_label=self.loc_label,
            loc_container=self.loc_container,
        )

    def set(
        self,
        value: typing.Tuple[
            str | None,
            str | None,
        ],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Sets the value of the input element.

        Parameters
        ----------
        value
            The value to set. The first element is the start date and the second element is the end date.
        timeout
            The maximum time to wait for the value to be set. Defaults to `None`.
        """
        start = value[0]
        end = value[1]
        # TODO-future; Composable set() methods?
        if start is not None:
            self.date_start.set(value=start, timeout=timeout)
        if end is not None:
            self.date_end.set(value=end, timeout=timeout)

    def expect_value(
        self,
        value: (
            typing.Tuple[PatternOrStr, PatternOrStr]
            | typing.Tuple[PatternOrStr, MISSING_TYPE]
            | typing.Tuple[MISSING_TYPE, PatternOrStr]
        ),
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected value.

        Parameters
        ----------
        value
            The expected value. The first element is the start date and the second element is the end date.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        if all_missing(*value):
            raise ValueError("Both `start_val` and `end_val` can not be `MISSING_TYPE`")
        start_val = value[0]
        end_val = value[1]
        # We can not use `[value={value}]` within Locators.
        # The physical `value` attribute is never set, so we can not select on it.
        # We must as the start and end values individually, rather than at the same time like the checkboxgroup input.
        # TODO-future; Composable expectations
        if not_is_missing(start_val):
            self.date_start.expect_value(start_val, timeout=timeout)
        if not_is_missing(end_val):
            self.date_end.expect_value(end_val, timeout=timeout)

    # min: Optional[Union[date, str]] = None,
    def expect_min_date(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected minimum date.

        Parameters
        ----------
        value
            The expected minimum date.
        timeout
            The maximum time to wait for the minimum date to appear. Defaults to `None`.
        """
        # TODO-future; Composable expectations
        self.date_start.expect_min_date(value, timeout=timeout)
        self.date_end.expect_min_date(value, timeout=timeout)

    # max: Optional[Union[date, str]] = None,
    def expect_max_date(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected maximum date.

        Parameters
        ----------
        value
            The expected maximum date.
        timeout
            The maximum time to wait for the maximum date to appear. Defaults to `None`.
        """
        # TODO-future; Composable expectations
        self.date_start.expect_max_date(value, timeout=timeout)
        self.date_end.expect_max_date(value, timeout=timeout)

    # format: str = "yyyy-mm-dd",
    def expect_format(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected format.

        Parameters
        ----------
        value
            The expected format.
        timeout
            The maximum time to wait for the format to appear. Defaults to `None`.
        """
        # TODO-future; Composable expectations
        self.date_start.expect_format(value, timeout=timeout)
        self.date_end.expect_format(value, timeout=timeout)

    # startview: str = "month",
    def expect_startview(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected start view.

        Parameters
        ----------
        value
            The expected start view.
        timeout
            The maximum time to wait for the start view to appear. Defaults to `None`.
        """
        # TODO-future; Composable expectations
        self.date_start.expect_startview(value, timeout=timeout)
        self.date_end.expect_startview(value, timeout=timeout)

    # weekstart: int = 0,
    def expect_weekstart(
        self,
        value: int | AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected week start.

        Parameters
        ----------
        value
            The expected week start.
        timeout
            The maximum time to wait for the week start to appear. Defaults to `None`.
        """
        # TODO-future; Composable expectations
        self.date_start.expect_weekstart(value, timeout=timeout)
        self.date_end.expect_weekstart(value, timeout=timeout)

    # language: str = "en",
    def expect_language(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected language.

        Parameters
        ----------
        value
            The expected language.
        timeout
            The maximum time to wait for the language to appear. Defaults to `None`.
        """
        # TODO-future; Composable expectations
        self.date_start.expect_language(value, timeout=timeout)
        self.date_end.expect_language(value, timeout=timeout)

    # separator: str = " to ",
    def expect_separator(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected separator.

        Parameters
        ----------
        value
            The expected separator.
        timeout
            The maximum time to wait for the separator to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_separator).to_have_text(value, timeout=timeout)

    # width: Optional[str] = None,

    # autoclose: bool = True,
    def expect_autoclose(
        self,
        value: Literal["true", "false"],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected autoclose value.

        Parameters
        ----------
        value
            The expected autoclose value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        # TODO-future; Composable expectations
        self.date_start.expect_autoclose(value, timeout=timeout)
        self.date_end.expect_autoclose(value, timeout=timeout)


######################################################
# # Outputs
######################################################


class _OutputBaseP(Protocol):
    id: str
    loc: Locator
    page: Page


class _OutputBase:
    """
    Base class for output controls.
    """

    id: str
    """
    The ID of the output control.
    """
    loc: Locator
    """
    Playwright `Locator` of the output control.
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
        self.id = id

        if isinstance(loc, str):
            loc = page.locator(loc)
        self.loc = loc

    @property
    # TODO; Return type
    def expect(self):
        return playwright_expect(self.loc)


class _OutputTextValue(_OutputBase):
    # cls = "shiny-text-output" + (" noplaceholder" if not placeholder else "")
    # return tags.pre(id=resolve_id(id), class_=cls)

    def expect_value(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the output has the expected value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        """Note this function will trim value and output text value before comparing them"""
        self.expect.to_have_text(value, timeout=timeout)


class _OutputContainerP(_OutputBaseP, Protocol):
    def expect_container_tag(
        self: _OutputBaseP,
        value: Literal["span", "div"] | str,
        *,
        timeout: Timeout = None,
    ) -> None: ...


class _OutputContainerM:
    def expect_container_tag(
        self: _OutputBaseP,
        value: Literal["span", "div"] | str,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the output has the expected container tag.

        Parameters
        ----------
        value
            The expected container tag.
        timeout
            The maximum time to wait for the container tag to appear. Defaults to `None`.
        """
        loc = self.loc.locator(f"xpath=self::{value}")
        playwright_expect(loc).to_have_count(1, timeout=timeout)


class _OutputInlineContainerM(_OutputContainerM):
    def expect_inline(
        self: _OutputContainerP,
        value: bool = False,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the output is inline.

        Parameters
        ----------
        value
            Whether the output is inline.
        timeout
            The maximum time to wait for the output to appear. Defaults to `None`.
        """
        tag_name = "span" if value else "div"
        self.expect_container_tag(tag_name, timeout=timeout)


class OutputText(
    _OutputInlineContainerM,
    _OutputTextValue,
):
    """Controller for :func:`shiny.ui.output_text`."""

    loc: Locator
    """
    Playwright `Locator` of the text output.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initializes a text output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the text output.
        """
        super().__init__(page, id=id, loc=f"#{id}.shiny-text-output")

    def get_value(self, *, timeout: Timeout = None) -> str:
        """
        Gets the text value of the output.

        Parameters
        ----------
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        return self.loc.inner_text(timeout=timeout)


class OutputCode(_OutputTextValue):
    """Controller for :func:`shiny.ui.output_code`."""

    loc: Locator
    """
    Playwright `Locator` of the code output.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a code output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the code output.
        """
        super().__init__(page, id=id, loc=f"pre#{id}.shiny-text-output")

    def expect_has_placeholder(
        self,
        value: bool = False,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the code output has the expected placeholder.

        Parameters
        ----------
        value
            Whether the code output has a placeholder.
        timeout
            The maximum time to wait for the placeholder to appear. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc,
            class_="noplaceholder",
            has_class=not value,
            timeout=timeout,
        )


class OutputTextVerbatim(_OutputTextValue):
    """Controller for :func:`shiny.ui.output_text_verbatim`."""

    loc: Locator
    """
    Playwright `Locator` of the verbatim text output.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a verbatim text output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the verbatim text output.
        """
        super().__init__(page, id=id, loc=f"pre#{id}.shiny-text-output")

    def expect_has_placeholder(
        self,
        value: bool = False,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the verbatim text output has the expected placeholder.

        Parameters
        ----------
        value
            Whether the verbatim text output has a placeholder.
        timeout
            The maximum time to wait for the placeholder to appear. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc,
            class_="noplaceholder",
            has_class=not value,
            timeout=timeout,
        )


class _OutputImageBase(_OutputInlineContainerM, _OutputBase):

    loc_img: Locator
    """
    Playwright `Locator` of the image.
    """

    def __init__(
        self,
        page: Page,
        id: str,
        loc_classes: str = "",
    ) -> None:
        """
        Initializes an image output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the image.
        loc_classes
            Additional classes to locate the image. Defaults to "".
        """
        super().__init__(
            page,
            id=id,
            loc=f"#{id}.shiny-image-output{loc_classes}",
        )
        self.loc_img = self.loc.locator("img")

    def expect_height(
        self,
        value: StyleValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the image has the expected height.

        Parameters
        ----------
        value
            The expected height.
        timeout
            The maximum time to wait for the height to appear. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc, "height", value, timeout=timeout)

    def expect_width(
        self,
        value: StyleValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the image has the expected width.

        Parameters
        ----------
        value
            The expected width.
        timeout
            The maximum time to wait for the width to appear. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc, "width", value, timeout=timeout)

    def expect_img_src(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the image has the expected src.

        Parameters
        ----------
        value
            The expected src.
        timeout
            The maximum time to wait for the src to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc_img, "src", value, timeout=timeout)

    def expect_img_width(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the image has the expected width.

        Parameters
        ----------
        value
            The expected width.
        timeout
            The maximum time to wait for the width to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc_img, "width", value, timeout=timeout)

    def expect_img_height(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the image has the expected height.

        Parameters
        ----------
        value
            The expected height.
        timeout
            The maximum time to wait for the height to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc_img, "height", value, timeout=timeout)

    def expect_img_alt(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the image has the expected alt text.

        Parameters
        ----------
        value
            The expected alt text.
        timeout
            The maximum time to wait for the alt text to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc_img, "alt", value, timeout=timeout)

    # def expect_img_style(
    #     self,
    #     value: AttrValue,
    #     *,
    #     timeout: Timeout = None,
    # ) -> None:
    #     expect_attr(self.loc_img, "style", value, timeout=timeout)


class OutputImage(_OutputImageBase):
    """Controller for :func:`shiny.ui.output_image`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes an image output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the image.
        """
        super().__init__(page, id=id)


class OutputPlot(_OutputImageBase):
    """Controller for :func:`shiny.ui.output_plot`."""

    loc: Locator
    """
    Playwright `Locator` of the plot output.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a plot output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the plot.
        """
        super().__init__(page, id=id, loc_classes=".shiny-plot-output")


class OutputUi(_OutputInlineContainerM, _OutputBase):
    """Controller for :func:`shiny.ui.output_ui`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a UI output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the UI output.
        """
        super().__init__(page, id=id, loc=f"#{id}")

    # TODO-future; Should we try verify that `recalculating` class is not present? Do this for all outputs!
    def expect_empty(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Asserts that the output is empty.

        Parameters
        ----------
        value
            Whether the output is empty.
        timeout
            The maximum time to wait for the output to be empty. Defaults to `None`.
        """
        if value:
            self.expect.to_be_empty(timeout=timeout)
        else:
            self.expect.not_to_be_empty(timeout=timeout)


# When making selectors, use `xpath` so that direct decendents can be checked
class OutputTable(_OutputBase):
    """Controller for :func:`shiny.ui.output_table`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a table output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the table.
        """
        super().__init__(page, id=id, loc=f"#{id}")

    def expect_cell(
        self,
        value: PatternOrStr,
        row: int,
        col: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the table cell has the expected text.

        Parameters
        ----------
        value
            The expected text in the cell.
        row
            The row number.
        col
            The column number.
        timeout
            The maximum time to wait for the text to appear. Defaults to `None`.
        """
        if not isinstance(row, int):
            raise TypeError("`row` must be an integer")
        if not isinstance(col, int):
            raise TypeError("`col` must be an integer")
        playwright_expect(
            self.loc.locator(
                f"xpath=./table/tbody/tr[{row}]/td[{col}] | ./table/tbody/tr[{row}]/th[{col}]"
            )
        ).to_have_text(value, timeout=timeout)

    def expect_column_labels(
        self,
        value: ListPatternOrStr | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the table has the expected column labels.

        Parameters
        ----------
        value
            The expected column labels. If None, it asserts that the table has no column labels.
        timeout
            The maximum time to wait for the column labels to appear. Defaults to `None`.
        """
        if isinstance(value, list) and len(value) == 0:
            value = None

        if value is None:
            playwright_expect(
                self.loc.locator("xpath=./table/thead/tr/th")
            ).to_have_count(0, timeout=timeout)
        else:
            playwright_expect(
                self.loc.locator("xpath=./table/thead/tr/th")
            ).to_have_text(value, timeout=timeout)

    def expect_column_text(
        self,
        col: int,
        # Can't use `None` as we don't know how many rows exist
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the column has the expected text.

        Parameters
        ----------
        col
            The column number.
        value
            The expected text in the column.
        timeout
            The maximum time to wait for the text to appear. Defaults to `None`.
        """
        if not isinstance(col, int):
            raise TypeError("`col` must be an integer")
        playwright_expect(
            self.loc.locator(f"xpath=./table/tbody/tr/td[{col}]")
        ).to_have_text(
            value,
            timeout=timeout,
        )

    def expect_ncol(
        self,
        value: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the table has the expected number of columns.

        Parameters
        ----------
        value
            The expected number of columns in the table.
        timeout
            The maximum time to wait for the table to have the expected number of columns. Defaults to `None`.
        """
        playwright_expect(
            # self.loc.locator("xpath=./table/thead/tr[1]/(td|th)")
            self.loc.locator("xpath=./table/thead/tr[1]/td | ./table/thead/tr[1]/th")
        ).to_have_count(
            value,
            timeout=timeout,
        )

    def expect_nrow(
        self,
        value: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the table has the expected number of rows.

        Parameters
        ----------
        value
            The expected number of rows in the table.
        timeout
            The maximum time to wait for the table to have the expected number of rows. Defaults to `None`.
        """
        playwright_expect(self.loc.locator("xpath=./table/tbody/tr")).to_have_count(
            value,
            timeout=timeout,
        )


class Sidebar(
    _WidthLocM,
    _UiWithContainer,
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


class _CardBodyP(_UiBaseP, Protocol):
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


class _CardFooterLayoutP(_UiBaseP, Protocol):
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


class _CardValueBoxFullScreenLayoutP(_OutputBaseP, Protocol):
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
    _WidthLocM,
    _CardValueBoxFullScreenM,
    _UiWithContainer,
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
    _WidthLocM,
    _CardFooterM,
    _CardBodyM,
    _CardValueBoxFullScreenM,
    _UiWithContainer,
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


class Accordion(
    _WidthLocM,
    _UiWithContainer,
):
    """Controller for :func:`shiny.ui.accordion`."""

    loc: Locator
    """
    Playwright `Locator` for each accordion items.
    """
    loc_container: Locator
    """
    Playwright `Locator` for the accordion container.
    """
    # loc_open: Locator
    # """
    # `Locator` for the open accordion panel
    # """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `Accordion` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the accordion.
        """
        super().__init__(
            page,
            id=id,
            loc="> div.accordion-item",
            loc_container=f"div#{id}.accordion.shiny-bound-input",
        )
        # self.loc_open = self.loc.locator(
        #     # Return self
        #     "xpath=.",
        #     # Simple approach as position is not needed
        #     has=page.locator(
        #         "> div.accordion-collapse.show",
        #     ),
        # )

    def expect_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expects the accordion to have the specified height.

        Parameters
        ----------
        value
            The expected height.
        timeout
            The maximum time to wait for the height to be visible and interactable. Defaults to `None`.
        """
        _expect_style_to_have_value(
            self.loc_container, "height", value, timeout=timeout
        )

    def expect_width(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expects the accordion to have the specified width.

        Parameters
        ----------
        value
            The expected width.
        timeout
            The maximum time to wait for the width to be visible and interactable. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc_container, "width", value, timeout=timeout)

    def expect_open(
        self,
        value: list[PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
        _MultipleDomItems.expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type=self.page.locator(
                "> div.accordion-item",
                has=self.page.locator("> div.accordion-collapse.show"),
            ),
            # el_type="> div.accordion-item:has(> div.accordion-collapse.show)",
            arr_name="value",
            arr=value,
            key="data-value",
            timeout=timeout,
        )

    def expect_panels(
        self,
        value: list[PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the accordion to have the specified panels.

        Parameters
        ----------
        value
            The expected panels.
        timeout
            The maximum time to wait for the panels to be visible and interactable. Defaults to `None`.
        """
        _MultipleDomItems.expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="> div.accordion-item",
            arr_name="value",
            arr=value,
            key="data-value",
            timeout=timeout,
        )

    def set(
        self,
        open: str | list[str],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Sets the state of the accordion panel.

        Parameters
        ----------
        open
            The open accordion panel(s).
        timeout
            The maximum time to wait for the accordion panel to be visible and interactable. Defaults to `None`.
        """
        if isinstance(open, str):
            open = [open]
        for element in self.loc.element_handles():
            element.wait_for_element_state(state="visible", timeout=timeout)
            element.scroll_into_view_if_needed(timeout=timeout)
            elem_value = element.get_attribute("data-value")
            if elem_value is None:
                raise ValueError(
                    "Accordion panel does not have a `data-value` attribute"
                )
            self.accordion_panel(elem_value).set(elem_value in open, timeout=timeout)

    def accordion_panel(
        self,
        data_value: str,
    ) -> AccordionPanel:
        """
        Returns the accordion panel (:class:`~shiny.playwright.controls.AccordionPanel`)
        with the specified data value.

        Parameters
        ----------
        data_value
            The data value of the accordion panel.
        """
        return AccordionPanel(self.page, self.id, data_value)


class AccordionPanel(
    _WidthLocM,
    _UiWithContainer,
):
    """
    Controller for :func:`shiny.ui.accordion_panel`.
    """

    loc_label: Locator
    """
    Playwright `Locator` for the accordion panel's label.
    """
    loc_icon: Locator
    """
    Playwright `Locator` for the accordion panel's icon.
    """
    loc_body: Locator
    """
    Playwright `Locator` for the accordion panel's body.
    """
    loc_header: Locator
    """
    Playwright `Locator` for the accordion panel's header.
    """
    # loc_body_visible: Locator
    # """
    # Playwright `Locator` for the visible accordion panel body
    # """

    def __init__(self, page: Page, id: str, data_value: str) -> None:
        """
        Initializes a new instance of the `AccordionPanel` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the accordion panel.
        data_value
            The data value of the accordion panel.
        """
        super().__init__(
            page,
            id=id,
            loc=f"> div.accordion-item[data-value='{data_value}']",
            loc_container=f"div#{id}.accordion.shiny-bound-input",
        )

        self.loc_label = self.loc.locator(
            "> .accordion-header > .accordion-button > .accordion-title"
        )

        self.loc_icon = self.loc.locator(
            "> .accordion-header > .accordion-button > .accordion-icon"
        )

        self.loc_body = self.loc.locator("> .accordion-collapse")
        self.loc_header = self.loc.locator("> .accordion-header")
        self._loc_body_visible = self.loc.locator("> .accordion-collapse.show")

    def expect_label(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the accordion panel label to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the label to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_label).to_have_text(value, timeout=timeout)

    def expect_body(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the accordion panel body to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the body to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_body).to_have_text(value, timeout=timeout)

    def expect_icon(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the accordion panel icon to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the icon to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_icon).to_have_text(value, timeout=timeout)

    def expect_open(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expects the accordion panel to be open or closed.

        Parameters
        ----------
        value
            `True` if the accordion panel is expected to be open, `False` otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc_body,
            "show",
            has_class=value,
            timeout=timeout,
        )

    # user sends value of Open: true | false
    def set(self, open: bool, *, timeout: Timeout = None) -> None:
        """
        Sets the state of the control to open or closed.

        Parameters
        ----------
        open
            `True` to open the accordion panel, False to close it.
        timeout
            The maximum time to wait for the control to be visible and interactable. Defaults to `None`.
        """
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        expect_not_to_have_class(self.loc_body, "collapsing", timeout=timeout)
        if self._loc_body_visible.count() != int(open):
            self._toggle(timeout=timeout)

    def _toggle(self, *, timeout: Timeout = None) -> None:
        """
        Toggles the state of the control.

        Parameters
        ----------
        timeout
            The maximum time to wait for the control to be visible and interactable. Defaults to `None`.
        """
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        self.loc_header.click(timeout=timeout)


class _OverlayBase(_UiBase):
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
            self._toggle()

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


class _NavPanelBase(_UiWithContainer):
    """A Base mixin class for Nav controls"""

    def nav_panel(
        self,
        value: str,
    ) -> NavPanel:
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
        _MultipleDomItems.expect_locator_values_in_list(
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


class NavPanel(_UiWithContainer):
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

    def __init__(self, page: Page, id: str, data_value: str) -> None:
        """
        Initializes a new instance of the `NavPanel` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the nav panel.
        data_value
            The data value of the nav panel.
        """
        super().__init__(
            page,
            id=id,
            loc=f"a[role='tab'][data-value='{data_value}']",
            loc_container=f"ul#{id}",
        )

        self._data_value: str = data_value

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
            f"div.tab-content[data-tabsetid='{datatab_id}'] > div.tab-pane[data-value='{self._data_value}']"
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


class NavsetTab(_NavPanelBase):
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


class NavsetPill(_NavPanelBase):
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


class NavsetUnderline(_NavPanelBase):
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


class NavsetPillList(_NavPanelBase):
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


class NavsetCardTab(_NavPanelBase):
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


class NavsetCardPill(_NavPanelBase):
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


class NavsetCardUnderline(_NavPanelBase):
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


class NavsetHidden(_NavPanelBase):
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


class NavsetBar(_NavPanelBase):
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


class Chat(_UiBase):
    """Controller for :func:`shiny.ui.chat`."""

    loc: Locator
    """
    Playwright `Locator` for the chat.
    """
    loc_messages: Locator
    """
    Playwright `Locator` for the chat messages.
    """
    loc_latest_message: Locator
    """
    Playwright `Locator` for the last message in the chat.
    """
    loc_input_container: Locator
    """
    Playwright `Locator` for the chat input container.
    """
    loc_input: Locator
    """
    Playwright `Locator` for the chat's <textarea> input.
    """
    loc_input_button: Locator
    """
    Playwright `Locator` for the chat's <button> input.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `Chat` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the chat.
        """
        super().__init__(
            page,
            id=id,
            loc=f"#{id}",
        )
        self.loc_messages = self.loc.locator("> shiny-chat-messages")
        self.loc_latest_message = self.loc_messages.locator("> :last-child")
        self.loc_input_container = self.loc.locator("> shiny-chat-input")
        self.loc_input = self.loc_input_container.locator("textarea")
        self.loc_input_button = self.loc_input_container.locator("button")

    def expect_latest_message(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the last message in the chat.

        Parameters
        ----------
        value
            The expected last message.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_latest_message).to_have_text(value, timeout=timeout)

    def expect_messages(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the chat messages.

        Parameters
        ----------
        value
            The expected messages.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_messages).to_have_text(value, timeout=timeout)

    def set_user_input(
        self,
        value: str,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Sets the user message in the chat.

        Parameters
        ----------
        value
            The message to send.
        timeout
            The maximum time to wait for the chat input to be visible and interactable. Defaults to `None`.
        """
        self.loc_input.type(value, timeout=timeout)

    def send_user_input(
        self, *, method: Literal["enter", "click"] = "enter", timeout: Timeout = None
    ) -> None:
        """
        Sends the user message in the chat.

        Parameters
        ----------
        method
            The method to send the user message. Defaults to `"enter"`.
        timeout
            The maximum time to wait for the chat input to be visible and interactable. Defaults to `None`.
        """
        if method == "enter":
            self.loc_input.press("Enter", timeout=timeout)
        else:
            self.loc_input_button.click(timeout=timeout)

    def expect_user_input(
        self, value: PatternOrStr, *, timeout: Timeout = None
    ) -> None:
        """
        Expects the user message in the chat.

        Parameters
        ----------
        value
            The expected user message.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_input).to_have_value(value, timeout=timeout)


class OutputDataFrame(_UiWithContainer):
    """
    Controller for :func:`shiny.ui.output_data_frame`.
    """

    loc_container: Locator
    """
    Playwright `Locator` for the data frame container.
    """
    loc: Locator
    """
    Playwright `Locator` for the data frame.
    """
    loc_head: Locator
    """
    Playwright `Locator` for the head of the data frame table.
    """
    loc_body: Locator
    """
    Playwright `Locator` for the body of the data frame table.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `OutputDataFrame` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the data frame.
        """
        super().__init__(
            page,
            id=id,
            loc_container=f"#{id}.html-fill-item",
            loc="> div > div.shiny-data-grid",
        )
        self.loc_head = self.loc.locator("> table > thead")
        self.loc_body = self.loc.locator("> table > tbody")
        self.loc_column_filter = self.loc_head.locator(
            "> tr.filters > th:not(.table-corner)"
        )
        self.loc_column_label = self.loc_head.locator(
            "> tr:not(.filters) > th:not(.table-corner)"
        )

    def cell_locator(self, row: int, col: int) -> Locator:
        """
        Returns the locator for a specific cell in the data frame.

        Parameters
        ----------
        row
            The row number of the cell.
        col
            The column number of the cell.
        """

        return (
            # Find the direct row
            self.loc_body.locator(f"> tr[data-index='{row}']")
            # Find all direct td's and th's (these are independent sets)
            .locator("> td, > th")
            # Remove all results that contain the `row-number` class
            .locator(
                # self
                "xpath=.",
                has=self.page.locator(
                    "xpath=self::*[not(contains(@class, 'row-number'))]"
                ),
            )
            # Return the first result
            .nth(col)
        )

    # TODO-barret; Should this be called `expect_row_count()`?
    def expect_nrow(self, value: int, *, timeout: Timeout = None):
        """
        Expects the number of rows in the data frame.

        Parameters
        ----------
        value
            The expected number of rows.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_body.locator("> tr")).to_have_count(
            value, timeout=timeout
        )

    def expect_selected_num_rows(self, value: int, *, timeout: Timeout = None):
        """
        Expects the number of selected rows in the data frame.

        Parameters
        ----------
        value
            The expected number of selected rows.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(
            self.loc_body.locator("tr[aria-selected=true]")
        ).to_have_count(value, timeout=timeout)

    def expect_selected_rows(self, rows: list[int], *, timeout: Timeout = None):
        """
        Expects the specified rows to be selected.

        Parameters
        ----------
        rows
            The row numbers.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        # * given container...
        # * Add that container has all known rows
        # * Verify that selected row count is of size N
        big_loc = self.loc_body
        assert len(rows) > 0
        for row in rows:
            big_loc = big_loc.locator(
                "xpath=.",  # return "self"
                has=self.page.locator(
                    f"> tr[data-index='{row}'][aria-selected='true']"
                ),
            )

        try:
            playwright_expect(
                big_loc.locator("> tr[aria-selected='true']")
            ).to_have_count(len(rows), timeout=timeout)
        except AssertionError as e:
            # Debug expections

            # Expecting container to exist (count = 1)
            playwright_expect(self.loc_body).to_have_count(1, timeout=timeout)

            for row in rows:
                # Expecting item `{item}` to exist in container
                # Perform exact matches on strings.
                playwright_expect(
                    # Simple approach as position is not needed
                    self.loc_body.locator(
                        f"> tr[aria-selected='true'][data-index='{row}']",
                    )
                ).to_have_count(1, timeout=timeout)

            # Could not find the reason why. Raising the original error.
            raise e

    def _expect_row_focus_state(
        self, in_focus: bool = True, *, row: int, timeout: Timeout = None
    ):
        """
        Expects the focus state of the specified row.

        Parameters
        ----------
        row
            The row number.
        in_focus
            `True` if the row is expected to be in focus, `False` otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if in_focus:
            playwright_expect(
                self.loc_body.locator(f"> tr[data-index='{row}']")
            ).to_be_focused(timeout=timeout)
        else:
            playwright_expect(
                self.loc_body.locator(f"> tr[data-index='{row}']")
            ).not_to_be_focused(timeout=timeout)

    def expect_cell(
        self,
        value: PatternOrStr,
        *,
        row: int,
        col: int,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the cell in the data frame to have the specified text.

        Parameters
        ----------
        value
            The expected text in the cell.
        row
            The row number of the cell.
        col
            The column number of the cell.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if not isinstance(row, int):
            raise TypeError("`row` must be an integer.")
        if not isinstance(col, int):
            raise TypeError("`col` must be an integer.")
        self._cell_scroll_if_needed(row=row, col=col, timeout=timeout)
        playwright_expect(self.cell_locator(row, col)).to_have_text(
            value, timeout=timeout
        )

    def expect_column_labels(
        self,
        value: ListPatternOrStr | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the column labels in the data frame.

        Parameters
        ----------
        value
            The expected column labels.

            Note: None if the column labels are expected to not exist.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if isinstance(value, list) and len(value) == 0:
            value = None

        if value is None:
            playwright_expect(self.loc_column_label).to_have_count(0, timeout=timeout)
        else:
            playwright_expect(self.loc_column_label).to_have_text(
                value, timeout=timeout
            )

    def _cell_scroll_if_needed(self, *, row: int, col: int, timeout: Timeout):
        """
        Scrolls the cell into view if needed.

        Parameters
        ----------
        row
            The row number of the cell.
        col
            The column number of the cell.
        timeout
            The maximum time to wait for the action to complete.
        """
        # Check first and last row data-index and make sure `row` is included

        cell = self.cell_locator(row=row, col=col)

        # Scroll down if top number is larger
        while not cell.is_visible(timeout=timeout):
            first_row = self.loc_body.locator("> tr[data-index]").first
            first_row_index = first_row.get_attribute("data-index")
            if first_row_index is None:
                break
            if int(first_row_index) >= row:
                first_row.scroll_into_view_if_needed(timeout=timeout)
            else:
                # First row index is lower than `row`
                break
        # Scroll up if bottom number is smaller
        while not cell.is_visible(timeout=timeout):
            last_row = self.loc_body.locator("> tr[data-index]").last
            last_row_index = last_row.get_attribute("data-index")
            if last_row_index is None:
                break
            if int(last_row_index) <= row:
                last_row.scroll_into_view_if_needed(timeout=timeout)
            else:
                # Last row index is higher than `row`
                break
        cell.scroll_into_view_if_needed(timeout=timeout)

    def _expect_column_label(
        self,
        value: ListPatternOrStr,
        *,
        col: int,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the text in the specified column of the data frame.

        Parameters
        ----------
        value
            The expected text in the column.
        col
            The column number.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if not isinstance(col, int):
            raise TypeError("`col` must be an integer.")
        # It's zero based, nth(0) selects the first element.
        playwright_expect(self.loc_column_label.nth(col - 1)).to_have_text(
            value,
            timeout=timeout,
        )

    def expect_ncol(
        self,
        value: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the number of columns in the data frame.

        Parameters
        ----------
        value
            The expected number of columns.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_column_label).to_have_count(
            value,
            timeout=timeout,
        )

    def expect_cell_class(
        self,
        value: str,
        *,
        row: int,
        col: int,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the class of the cell

        Parameters
        ----------
        value
            The expected class of the cell.
        row
            The row number of the cell.
        col
            The column number of the cell.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        expect_to_have_class(
            self.cell_locator(row=row, col=col),
            value,
            timeout=timeout,
        )

    def select_rows(
        self,
        value: list[int],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Selects the rows in the data frame.

        Parameters
        ----------
        value
            The list of row numbers to select.
        timeout
            The maximum time to wait for the action to complete. Defaults to `None`.
        """
        if len(value) > 1:
            value = sorted(value)
            # check if the items in the row contain all numbers from index 0 to index -1
            if value == list(range(value[0], value[-1] + 1)):
                self.page.keyboard.down("Shift")
                self.cell_locator(row=value[0], col=0).click(timeout=timeout)
                self.cell_locator(row=value[-1], col=0).click(timeout=timeout)
                self.page.keyboard.up("Shift")
            else:
                # if operating system is MacOs use Meta (Cmd) else use Ctrl key
                if platform.system() == "Darwin":
                    self.page.keyboard.down("Meta")
                else:
                    self.page.keyboard.down("Control")
                for row in value:
                    self._cell_scroll_if_needed(row=row, col=0, timeout=timeout)
                    self.cell_locator(row=row, col=0).click(timeout=timeout)
                if platform.system() == "Darwin":
                    self.page.keyboard.up("Meta")
                else:
                    self.page.keyboard.up("Control")
        else:
            self.cell_locator(row=value[0], col=0).click(timeout=timeout)

    def expect_class_state(
        self,
        value: str,
        *,
        row: int,
        col: int,
        timeout: Timeout = None,
    ):
        """
        Expects the state of the class in the data frame.

        Parameters
        ----------
        value
            The expected state of the class.
        row
            The row number of the cell.
        col
            The column number of the cell.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if value == "ready":
            playwright_expect(self.cell_locator(row=row, col=col)).not_to_have_class(
                "cell-edit-editing", timeout=timeout
            )
        elif value == "editing":
            self.expect_cell_class("cell-edit-editing", row=row, col=col)
        elif value == "saving":
            self.expect_cell_class("cell-edit-saving", row=row, col=col)
        elif value == "failure":
            self.expect_cell_class("cell-edit-failure", row=row, col=col)
        elif value == "success":
            self.expect_cell_class("cell-edit-success", row=row, col=col)
        else:
            raise ValueError(
                "Invalid state. Select one of 'success', 'failure', 'saving', 'editing', 'ready'"
            )

    def _edit_cell_no_save(
        self,
        text: str,
        *,
        row: int,
        col: int,
        timeout: Timeout = None,
    ) -> None:
        """
        Edits the cell in the data frame.

        Parameters
        ----------
        value
            The value to edit in the cell.
        row
            The row number of the cell.
        col
            The column number of the cell.
        timeout
            The maximum time to wait for the action to complete. Defaults to `None`.
        """
        cell = self.cell_locator(row=row, col=col)

        self._cell_scroll_if_needed(row=row, col=col, timeout=timeout)
        cell.dblclick(timeout=timeout)
        cell.locator("> textarea").fill(text)

    def set_sort(
        self,
        sort: int | ColumnSort | list[int | ColumnSort] | None,
        *,
        timeout: Timeout = None,
    ):
        """
        Set or modify the sorting of columns in a table or grid component.
        This method allows setting single or multiple column sorts, or resetting the sort order.

        Parameters
        ----------
        sort
            The sorting configuration to apply. Can be one of the following:
                * `int`: Index of the column to sort by (ascending order by default).
                * `ColumnSort`: A dictionary specifying a single column sort with 'col' and 'desc' keys.
                * `list[int | ColumnSort]`: A list of ints or dictionaries for multi-column sorting.
                * `None`: No sorting applied (not implemented in the current code).

            If a `desc` values is provided within your `ColumnSort` shaped dictionary, then the direction will be set to that value. If no `desc` value is provided, the column will be sorted in the default sorting order.
        timeout
            The maximum time to wait for the action to complete. Defaults to `None`.
        """

        def click_loc(loc: Locator, *, shift: bool = False):
            clickModifier: list[Literal["Shift"]] | None = (
                ["Shift"] if bool(shift) else None
            )
            loc.click(
                timeout=timeout,
                modifiers=clickModifier,
            )
            # Wait for arrows to react a little bit
            # This could possible be changed to a `wait_for_change`, but 150ms should be fine
            self.page.wait_for_timeout(150)

        # Reset arrow sorting by clicking on the arrows until none are found
        sortingArrows = self.loc_column_label.locator("svg.sort-arrow")
        while sortingArrows.count() > 0:
            click_loc(sortingArrows.first)

        # Quit early if no sorting is needed
        if sort is None:
            return

        if isinstance(sort, int) | isinstance(sort, dict) and not isinstance(
            sort, list
        ):
            sort = [sort]

        if not isinstance(sort, list):
            raise ValueError(
                "Invalid sort value. Must be an int, ColumnSort, list[ColumnSort], or None."
            )

        # For every sorting info...
        for sort_info, i in zip(sort, range(len(sort))):
            # TODO-barret-future; assert column does not have `cell-html` class
            shift = i > 0

            if isinstance(sort_info, int):
                sort_info = {"col": sort_info}

            # Verify ColumnSortInfo
            assert isinstance(
                sort_info, dict
            ), f"Invalid sort value at position {i}. Must be an int, ColumnSort, list[ColumnSort], or None."
            assert (
                "col" in sort_info
            ), f"Column index (`col`) at position {i} is required for sorting."

            sort_col = self.loc_column_label.nth(sort_info["col"])
            expect_not_to_have_class(sort_col, "header-html")

            # If no `desc` key is found, click the column to sort and move on
            if "desc" not in sort_info:
                click_loc(sort_col, shift=shift)
                continue

            # "desc" in sort_info
            desc_val = bool(sort_info["desc"])
            sort_col.scroll_into_view_if_needed()
            for _ in range(2):
                if desc_val:
                    # If a descending is found, stop clicking
                    if sort_col.locator("svg.sort-arrow-down").count() > 0:
                        break
                else:
                    # If a ascending is found, stop clicking
                    if sort_col.locator("svg.sort-arrow-up").count() > 0:
                        break
                click_loc(sort_col, shift=shift)

    # TODO-karan-test: Add support for a list of columns ? If so, all other columns should be reset
    def set_filter(
        self,
        # TODO-barret support array of filters
        filter: ColumnFilter | list[ColumnFilter] | None,
        *,
        timeout: Timeout = None,
    ):
        """
        Set or reset filters for columns in a table or grid component.
        This method allows setting string filters, numeric range filters, or clearing all filters.

        Parameters
        ----------
        filter
            The filter to apply. Can be one of the following:
                * `None`: Resets all filters.
                * `ColumnFilterStr`: A dictionary specifying a string filter with 'col' and 'value' keys.
                * `ColumnFilterNumber`: A dictionary specifying a numeric range filter with 'col' and 'value' keys.
        timeout
            The maximum time to wait for the action to complete. Defaults to `None`.
        """
        # reset all filters
        all_input_handles = self.loc_column_filter.locator(
            "> input, > div > input"
        ).element_handles()
        for input_handle in all_input_handles:
            input_handle.scroll_into_view_if_needed()
            input_handle.fill("", timeout=timeout)

        if filter is None:
            return

        if isinstance(filter, dict):
            filter = [filter]

        if not isinstance(filter, list):
            raise ValueError(
                "Invalid filter value. Must be a ColumnFilter, list[ColumnFilter], or None."
            )

        for filterInfo in filter:
            if "col" not in filterInfo:
                raise ValueError("Column index (`col`) is required for filtering.")

            if "value" not in filterInfo:
                raise ValueError("Filter value (`value`) is required for filtering.")

            filterColumn = self.loc_column_filter.nth(filterInfo["col"])

            if isinstance(filterInfo["value"], str):
                filterColumn.locator("> input").fill(filterInfo["value"])
            elif isinstance(filterInfo["value"], (tuple, list)):
                header_inputs = filterColumn.locator("> div > input")
                if filterInfo["value"][0] is not None:
                    header_inputs.nth(0).fill(
                        str(filterInfo["value"][0]),
                        timeout=timeout,
                    )
                if filterInfo["value"][1] is not None:
                    header_inputs.nth(1).fill(
                        str(filterInfo["value"][1]),
                        timeout=timeout,
                    )
            else:
                raise ValueError(
                    "Invalid filter value. Must be a string or a tuple/list of two numbers."
                )

    def set_cell(
        self,
        text: str,
        *,
        row: int,
        col: int,
        finish_key: (
            Literal["Enter", "Shift+Enter", "Tab", "Shift+Tab", "Escape"] | None
        ) = None,
        timeout: Timeout = None,
    ) -> None:
        """
        Saves the value of the cell in the data frame.

        Parameters
        ----------
        text
            The key to save the value of the cell.
        row
            The row number of the cell.
        col
            The column number of the cell.
        finish_key
            The key to save the value of the cell. If `None` (the default), no key will
            be pressed and instead the page body will be clicked.
        timeout
            The maximum time to wait for the action to complete. Defaults to `None`.
        """
        self._edit_cell_no_save(text, row=row, col=col, timeout=timeout)
        if finish_key is None:
            self.page.locator("body").click()
        else:
            self.cell_locator(row=row, col=col).locator("> textarea").press(finish_key)

    def expect_cell_title(
        self,
        value: str,
        *,
        row: int,
        col: int,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the validation message of the cell in the data frame, which will be in
        the `title` attribute of the element.

        Parameters
        ----------
        value
            The expected validation message of the cell.
        row
            The row number of the cell.
        col
            The column number of the cell.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.cell_locator(row=row, col=col)).to_have_attribute(
            name="title", value=value, timeout=timeout
        )


# TODO: Use mixin for dowloadlink and download button
class DownloadLink(_InputActionBase):
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
    _WidthLocM,
    _InputActionBase,
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
