"""Facade classes for working with Shiny inputs/outputs in Playwright"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import time
import typing
from typing import Literal, Optional, Protocol

from playwright.sync_api import FilePayload, FloatRect, Locator, Page, Position
from playwright.sync_api import expect as playwright_expect

# Import `shiny`'s typing extentions.
# Since this is a private file, tell pyright to ignore the import
# (Imports split over many import statements due to auto formatting)
from shiny._typing_extensions import (
    TypeGuard,  # pyright: ignore[reportPrivateImportUsage]
)
from shiny._typing_extensions import (
    assert_type,  # pyright: ignore[reportPrivateImportUsage]
)
from shiny.types import MISSING, MISSING_TYPE

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


OptionalStr = Optional[str]
OptionalInt = Optional[int]
OptionalFloat = Optional[float]
OptionalBool = Optional[bool]

PatternStr = typing.Pattern[str]
PatternOrStr = typing.Union[str, PatternStr]
ListPatternOrStr = typing.Union[
    typing.List[PatternOrStr], typing.List[str], typing.List[PatternStr]
]
AttrValue = typing.Union[PatternOrStr, None]
StyleValue = typing.Union[PatternOrStr, None]

Timeout = typing.Union[float, None]
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
    # TODO-future; Composable set() method
    loc.fill("", timeout=timeout)  # Reset the value
    loc.type(text, delay=delay, timeout=timeout)  # Type the value


def expect_attr(
    loc: Locator,
    name: str,
    value: AttrValue,
    timeout: Timeout = None,
) -> None:
    """Expect an attribute to have a value. If `value` is `None`, then the attribute should not exist."""
    if value is None:
        # if isinstance(value, type(None)):
        # Not allowed to have any value for the attribute
        playwright_expect(loc).not_to_have_attribute(
            name, re.compile(r".*"), timeout=timeout
        )
        return

    playwright_expect(loc).to_have_attribute(name=name, value=value, timeout=timeout)


def _expect_class_value(
    loc: Locator,
    cls: str,
    has_class: bool,
    timeout: Timeout = None,
) -> None:
    """Expect a locator to have (or not to have) a class value"""
    if has_class:
        expect_to_have_class(loc, cls, timeout=timeout)
    else:
        expect_not_to_have_class(loc, cls, timeout=timeout)


def expect_to_have_class(
    loc: Locator,
    cls: str,
    timeout: Timeout = None,
) -> None:
    """Expect a locator to contain a class value"""
    cls_regex = re.compile(rf"(^|\s+){re.escape(cls)}(\s+|$)")
    playwright_expect(loc).to_have_class(cls_regex, timeout=timeout)


def expect_not_to_have_class(
    loc: Locator,
    cls: str,
    timeout: Timeout = None,
) -> None:
    """Expect a locator not to contain a class value"""
    cls_regex = re.compile(rf"(^|\s+){re.escape(cls)}(\s+|$)")
    playwright_expect(loc).not_to_have_class(cls_regex, timeout=timeout)


def _style_match_str(key: str, value: PatternOrStr) -> PatternStr:
    if isinstance(value, str):
        value_str = re.escape(value)
    else:
        value_str = value.pattern
    return re.compile(rf"(^|;)\s*{re.escape(key)}\s*:\s*{value_str}\s*(;|$)")


def _attr_match_str(key: str, value: str) -> str:
    # Escape double quotes
    value_str = value.replace('"', '\\"')
    # `key` is `value`
    return f'{key}="{value_str}"'
    # assert_type(value, re.Pattern[str])
    # # `key` contains `value`
    # return f'{key}*="{value.pattern}"'


def _xpath_match_str(key: str, value: PatternOrStr) -> str:
    if isinstance(value, str):
        # Escape double quotes
        value_str = value.replace('"', '\\"')
        # `key` is `value`
        return f'@{key}="{value_str}"'
    else:
        # Disabling type assertion for earlier versions of Python
        if sys.version_info >= (3, 10):
            assert_type(value, re.Pattern[str])

        # `key` contains `value`
        return f'matches(@{key}, "{value.pattern}")'


def expect_to_have_style(
    loc: Locator,
    css_key: str,
    # Str representation for value. Will be put in a regex with `css_key`
    css_value: StyleValue,
    timeout: Timeout = None,
) -> None:
    """Expect the `style` attribute to have a value. If `value` is `None`, then the style attribute should not exist."""
    if css_value is None:
        # Not allowed to have any value for the style
        playwright_expect(loc).not_to_have_attribute(
            "style",
            re.compile(rf"\b{re.escape(css_key)}\s*:"),
            timeout=timeout,
        )
        return

    playwright_expect(loc).to_have_attribute(
        "style",
        _style_match_str(css_key, css_value),
        timeout=timeout,
    )


def _expect_multiple(loc: Locator, multiple: bool, timeout: Timeout = None) -> None:
    value = "True" if multiple else None
    expect_to_have_style(loc, "multiple", value, timeout=timeout)


######################################################
# # Inputs
######################################################


class _InputBaseP(Protocol):
    id: str
    loc: Locator
    page: Page


class _InputWithContainerP(_InputBaseP, Protocol):
    loc_container: Locator


class _InputBase:
    # timeout: Timeout
    id: str
    loc: Locator
    page: Page

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
        return playwright_expect(self.loc)


class _InputWithContainer(_InputBase):
    loc_container: Locator

    def __init__(
        self,
        page: Page,
        *,
        id: str,
        loc: InitLocator,
        loc_container: InitLocator = "div.shiny-input-container",
    ) -> None:
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


class _InputWithLabel(_InputWithContainer):
    def __init__(
        self,
        page: Page,
        *,
        id: str,
        loc: InitLocator,
        loc_container: InitLocator = "div.shiny-input-container",
        loc_label: InitLocator | None = None,
    ) -> None:
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
        playwright_expect(self.loc_label).to_have_text(value, timeout=timeout)


class _WidthLocM:
    def expect_width(
        self: _InputBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "width", value=value, timeout=timeout)


class _WidthContainerM:
    def expect_width(
        self: _InputWithContainerP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc_container, "width", value=value, timeout=timeout)


class _SetTextM:
    def set(self: _InputBaseP, value: str, *, timeout: Timeout = None) -> None:
        set_text(self.loc, value, timeout=timeout)


class _ExpectTextInputValueM:
    def expect_value(
        self: _InputBaseP,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        playwright_expect(self.loc).to_have_value(value, timeout=timeout)


class InputNumeric(
    _SetTextM,
    _ExpectTextInputValueM,
    _WidthLocM,
    _InputWithLabel,
):
    # id: str,
    # label: TagChild,
    # value: float,
    # *,
    # min: Optional[float] = None,
    # max: Optional[float] = None,
    # step: Optional[float] = None,
    # width: Optional[str] = None,
    def __init__(self, page: Page, id: str) -> None:
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
        expect_attr(self.loc, "min", value=value, timeout=timeout)

    def expect_max(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "max", value=value, timeout=timeout)

    def expect_step(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "step", value=value, timeout=timeout)


class _ExpectSpellcheckAttrM:
    def expect_spellcheck(
        self: _InputBaseP,
        value: Literal["true", "false"] | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        # self.spellcheck.expect_to_have_value(value, timeout=timeout)
        expect_attr(self.loc, "spellcheck", value=value, timeout=timeout)


class _ExpectPlaceholderAttrM:
    def expect_placeholder(
        self: _InputBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "placeholder", value=value, timeout=timeout)


class _ExpectAutocompleteAttrM:
    def expect_autocomplete(
        self: _InputBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "autocomplete", value=value, timeout=timeout)


class InputText(
    _SetTextM,
    _ExpectTextInputValueM,
    _WidthLocM,
    _ExpectPlaceholderAttrM,
    _ExpectAutocompleteAttrM,
    _ExpectSpellcheckAttrM,
    _InputWithLabel,
):
    # id: str,
    # label: TagChild,
    # value: str = "",
    # *,
    # width: Optional[str] = None,
    # placeholder: Optional[str] = None,
    # autocomplete: Optional[str] = "off",
    # spellcheck: Optional[Literal["true", "false"]] = None,
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}[type=text].shiny-bound-input",
        )


class InputPassword(
    _SetTextM,
    _ExpectTextInputValueM,
    _ExpectPlaceholderAttrM,
    _InputWithLabel,
):
    # id: str,
    # label: TagChild,
    # value: str = "",
    # *,
    # width: Optional[str] = None,
    # placeholder: Optional[str] = None,
    ...

    def __init__(self, page: Page, id: str) -> None:
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
        expect_to_have_style(self.loc_container, "width", value, timeout=timeout)


Resize = Literal["none", "both", "horizontal", "vertical"]


class InputTextArea(
    _SetTextM,
    _ExpectTextInputValueM,
    _ExpectPlaceholderAttrM,
    _ExpectAutocompleteAttrM,
    _ExpectSpellcheckAttrM,
    _InputWithLabel,
):
    # id: str,
    # label: TagChild,
    # value: str = "",
    # width: Optional[str] = None,
    # height: Optional[str] = None,
    # cols: Optional[int] = None,
    # rows: Optional[int] = None,
    # placeholder: Optional[str] = None,
    # resize: Optional[
    #     Literal["none", "both", "horizontal", "vertical"]
    # ] = None,
    # autocomplete: Optional[str] = None,
    # spellcheck: Optional[Literal["true", "false"]] = None,
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"textarea#{id}.shiny-bound-input",
        )

    def expect_width(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        if value is None:
            expect_to_have_style(self.loc_container, "width", None, timeout=timeout)
            expect_to_have_style(self.loc, "width", "100%", timeout=timeout)
        else:
            expect_to_have_style(self.loc_container, "width", value, timeout=timeout)
            expect_to_have_style(self.loc, "width", None, timeout=timeout)

    def expect_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        expect_to_have_style(self.loc, "height", value, timeout=timeout)

    def expect_cols(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(self.loc, "cols", value=value, timeout=timeout)

    def expect_rows(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(self.loc, "rows", value=value, timeout=timeout)

    def expect_resize(
        self,
        value: Resize | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "resize", value=value, timeout=timeout)

    def expect_autoresize(
        self,
        value: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        _expect_class_value(
            self.loc,
            "textarea-autoresize",
            value,
            timeout=timeout,
        )


class _InputSelectBase(
    _WidthLocM,
    _InputWithLabel,
):
    loc_selected: Locator
    loc_choices: Locator
    loc_choice_groups: Locator

    def __init__(
        self,
        page: Page,
        id: str,
        *,
        select_class: str = "",
    ) -> None:
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
        selected: str | list[str],
        *,
        timeout: Timeout = None,
    ) -> None:
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
        """Expect choices to be in order"""
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
        selected: PatternOrStr | ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """Expect choices to be in order"""
        # Playwright doesn't like lists of size 0
        if isinstance(selected, list) and len(selected) == 0:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        if isinstance(selected, list):
            self.expect.to_have_values(selected, timeout=timeout)
        else:
            self.expect.to_have_value(selected, timeout=timeout)

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
        """Expect choices to be in order"""
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
        choice_labels: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if len(choice_labels) == 0:
            playwright_expect(self.loc_choices).to_have_count(0, timeout=timeout)
            return
        playwright_expect(self.loc_choices).to_have_text(choice_labels, timeout=timeout)

    # multiple: bool = False,
    def expect_multiple(self, multiple: bool, *, timeout: Timeout = None) -> None:
        _expect_multiple(self.loc, multiple, timeout=timeout)

    def expect_size(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(
            self.loc,
            "size",
            value=value,
            timeout=timeout,
        )


class InputSelect(_InputSelectBase):
    # id: str,
    # label: TagChild,
    # choices: SelectChoicesArg,
    # selected: Optional[Union[str, list[str]]] = None,
    # multiple: bool = False,
    # selectize: bool = False,
    # width: Optional[str] = None,
    # size: Optional[str] = None,
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            select_class=".form-select",
        )

    # selectize: bool = False,
    def expect_selectize(self, selectize: bool, *, timeout: Timeout = None) -> None:
        # class_=None if selectize else "form-select",
        _expect_class_value(
            self.loc,
            "form-select",
            has_class=not selectize,
            timeout=timeout,
        )


class InputSelectize(_InputSelectBase):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            select_class="",
        )


class _InputActionBase(_InputBase):
    def expect_label(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """Must include icon if present"""

        self.expect.to_have_text(value, timeout=timeout)

    def click(self, *, timeout: Timeout = None, **kwargs: object) -> None:
        self.loc.click(timeout=timeout, **kwargs)  # pyright: ignore[reportArgumentType]


class InputActionButton(
    _WidthLocM,
    _InputActionBase,
):
    # label: TagChild,
    # icon: TagChild = None,
    # width: Optional[str] = None,

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"button#{id}.action-button.shiny-bound-input",
        )


class InputActionLink(_InputActionBase):
    # label: TagChild,
    # icon: TagChild = None,

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
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
    _InputWithLabel,
):
    # label: TagChild
    # value: bool = False
    # width: Optional[str] = None
    def __init__(
        self, page: Page, id: str, loc: InitLocator, loc_label: str | None
    ) -> None:
        super().__init__(
            page,
            id=id,
            loc=loc,
            loc_label=loc_label,
        )

    def set(self, value: bool, *, timeout: Timeout = None, **kwargs: object) -> None:
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        self.loc.set_checked(
            value, timeout=timeout, **kwargs  # pyright: ignore[reportArgumentType]
        )

    def toggle(self, *, timeout: Timeout = None, **kwargs: object) -> None:
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        self.loc.click(timeout=timeout, **kwargs)  # pyright: ignore[reportArgumentType]

    def expect_checked(self, value: bool, *, timeout: Timeout = None) -> None:
        if value:
            self.expect.to_be_checked(timeout=timeout)
        else:
            self.expect.not_to_be_checked(timeout=timeout)


class InputCheckbox(_InputCheckboxBase):
    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"div.checkbox > label > input#{id}[type=checkbox].shiny-bound-input",
            loc_label="label > span",
        )


class InputSwitch(_InputCheckboxBase):
    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"div.form-switch > input#{id}[type=checkbox].shiny-bound-input",
            loc_label=f"label[for={id}]",
        )


class _MultipleDomItems:
    @staticmethod
    def assert_arr_is_unique(
        arr: ListPatternOrStr,
        msg: str,
    ) -> None:
        assert len(arr) == len(list(dict.fromkeys(arr))), msg

    @staticmethod
    def checked_css_str(
        is_checked: bool | MISSING_TYPE = MISSING,
    ) -> str:
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
        # Make sure the locator contains all of `arr`

        assert_type(arr, typing.List[str])

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


class _RadioButtonCheckboxGroupBase(_InputWithLabel):
    loc_choice_labels: Locator

    def expect_choice_labels(
        self,
        labels: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        if len(labels) == 1:
            labels_val = labels[0]
        else:
            labels_val = labels
        playwright_expect(self.loc_choice_labels).to_have_text(
            labels_val,
            timeout=timeout,
        )

    def expect_inline(self, inline: bool, *, timeout: Timeout = None) -> None:
        _expect_class_value(
            self.loc_container,
            "shiny-input-container-inline",
            has_class=inline,
            timeout=timeout,
        )


class InputCheckboxGroup(
    _WidthContainerM,
    _RadioButtonCheckboxGroupBase,
):
    # label: TagChild,
    # choices: ChoicesArg,
    # selected: Optional[Union[str, list[str]]] = None,
    # inline: bool = False,
    # width: Optional[str] = None,
    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
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
        # Allow `selected` to be a single Pattern to perform matching against many items
        selected: list[str],
        *,
        timeout: Timeout = None,
        **kwargs: object,
    ) -> None:
        # Having an arr of size 0 is allowed. Will uncheck everything
        assert_type(selected, typing.List[str])

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
        choices: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        _MultipleDomItems.expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="input[type=checkbox]",
            arr_name="choices",
            arr=choices,
            timeout=timeout,
        )

    def expect_selected(
        self,
        selected: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        # Playwright doesn't like lists of size 0
        if len(selected) == 0:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        _MultipleDomItems.expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="input[type=checkbox]",
            arr_name="selected",
            arr=selected,
            timeout=timeout,
            is_checked=True,
        )


class InputRadioButtons(
    _WidthContainerM,
    _RadioButtonCheckboxGroupBase,
):
    # id: str,
    # label: TagChild,
    # choices: ChoicesArg,
    # selected: Optional[str] = None,
    # inline: bool = False,
    # width: Optional[str] = None,
    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
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
        assert_type(selected, str)
        # Only need to set.
        # The Browser will _unset_ the previously selected radio button
        self.loc_container.locator(
            f"label input[type=radio][{_attr_match_str('value', selected)}]"
        ).check(timeout=timeout)

    def expect_choices(
        self,
        choices: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        _MultipleDomItems.expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="input[type=radio]",
            arr_name="choices",
            arr=choices,
            timeout=timeout,
        )

    def expect_selected(
        self,
        selected: PatternOrStr | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if selected is None:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        playwright_expect(self.loc_selected).to_have_value(selected, timeout=timeout)


class InputFile(
    # _ExpectPlaceholderAttrM,
    _InputWithLabel,
):
    loc_button: Locator
    loc_file_display: Locator
    loc_progress: Locator

    # id: str,
    # label: TagChild,
    # *,
    # multiple: bool = False,
    # accept: Optional[Union[str, list[str]]] = None,
    # width: Optional[str] = None,
    # button_label: str = "Browse...",
    # placeholder: str = "No file selected",
    # capture: Optional[Literal["environment", "user"]] = None,
    # with page.expect_file_chooser() as fc_info:
    #     page.get_by_text("Upload").click()
    # file_chooser = fc_info.value
    # file_chooser.set_files("myfile.pdf")
    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
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
        file_path: str
        | pathlib.Path
        | FilePayload
        | list[str | pathlib.Path]
        | list[FilePayload],
        *,
        timeout: Timeout = None,
        expect_complete_timeout: Timeout = 30 * 1000,
    ) -> None:
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
        expect_to_have_style(self.loc_progress, "width", "100%", timeout=timeout)

    # TODO-future; Test multiple file upload
    def expect_multiple(self, multiple: bool, *, timeout: Timeout = None) -> None:
        _expect_multiple(self.loc, multiple, timeout=timeout)

    def expect_accept(
        self,
        accept: list[str] | AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        if isinstance(accept, list):
            accept = ",".join(accept)
        expect_attr(self.loc, "accept", accept, timeout=timeout)

    def expect_width(self, width: StyleValue, *, timeout: Timeout = None) -> None:
        expect_to_have_style(self.loc_container, "width", width, timeout=timeout)

    def expect_button_label(
        self,
        button_label: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        playwright_expect(self.loc_button).to_have_text(button_label, timeout=timeout)

    def expect_capture(
        self,
        capture: Literal["environment", "user"] | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "capture", capture, timeout=timeout)

    def expect_placeholder(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(self.loc_file_display, "placeholder", value=value, timeout=timeout)


class _InputSliderBase(_WidthLocM, _InputWithLabel):
    # id: str,
    # label: TagChild,
    # min: SliderValueArg,
    # max: SliderValueArg,
    # value: Union[SliderValueArg, Iterable[SliderValueArg]],
    # step: Optional[SliderStepArg] = None,
    # ticks: bool = True,
    # animate: Union[bool, AnimationOptions] = False,
    # width: Optional[str] = None,
    # sep: str = ",",
    # pre: Optional[str] = None,
    # post: Optional[str] = None,
    # time_format: Optional[str] = None,
    # timezone: Optional[str] = None,
    # drag_range: bool = True,

    loc_irs: Locator
    loc_irs_ticks: Locator
    loc_play_pause: Locator

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
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
        if value is None:
            playwright_expect(self.loc_irs_ticks).to_have_count(0)
            return

        playwright_expect(self.loc_irs_ticks).to_have_text(value, timeout=timeout)

    def expect_animate(self, exists: bool, *, timeout: Timeout = None) -> None:
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
            expect_attr(
                self.loc_play_pause,
                "data-loop",
                "" if loop else None,
                timeout=timeout,
            )
        if not_is_missing(interval):
            expect_attr(
                self.loc_play_pause,
                "data-interval",
                str(interval),
                timeout=timeout,
            )

    # No `toggle` method as short animations with no loops can cause the button to
    # become `play` over and over again. Instead, have explicit `play` and `pause`
    # methods.
    def click_play(self, *, timeout: Timeout = None) -> None:
        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)
        _expect_class_value(
            self.loc_play_pause, "playing", has_class=False, timeout=timeout
        )
        self.loc_play_pause.click()

    def click_pause(self, *, timeout: Timeout = None) -> None:
        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)
        _expect_class_value(
            self.loc_play_pause, "playing", has_class=True, timeout=timeout
        )
        self.loc_play_pause.click()

    def expect_min(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(self.loc, "data-min", value=value, timeout=timeout)

    def expect_max(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(self.loc, "data-max", value=value, timeout=timeout)

    def expect_step(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(self.loc, "data-step", value=value, timeout=timeout)

    def expect_ticks(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(self.loc, "data-grid", value=value, timeout=timeout)

    def expect_sep(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(self.loc, "data-prettify-separator", value=value, timeout=timeout)

    def expect_pre(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(self.loc, "data-prefix", value=value, timeout=timeout)

    def expect_post(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(self.loc, "data-postfix", value=value, timeout=timeout)

    # def expect_data_type(
    #     self, value: AttrValue, *, timeout: Timeout = None
    # ) -> None:
    #     expect_attr(self.loc, "data-data-type", value=value, timeout=timeout)

    def expect_time_format(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(self.loc, "data-time-format", value=value, timeout=timeout)

    def expect_timezone(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(self.loc, "data-timezone", value=value, timeout=timeout)

    def expect_drag_range(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        expect_attr(self.loc, "data-drag-interval", value=value, timeout=timeout)

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
    loc_irs_label: Locator

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        super().__init__(page, id=id)
        self.loc_irs_label = self.loc_irs.locator("> .irs > .irs-single")

    def expect_value(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        playwright_expect(self.loc_irs_label).to_have_text(value, timeout=timeout)

    def set(
        self,
        value: str,
        *,
        max_err_values: int = 15,
        timeout: Timeout = None,
    ) -> None:
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
    loc_irs_label_from: Locator
    loc_irs_label_to: Locator

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        super().__init__(page, id=id)
        self.loc_irs_label_from = self.loc_irs.locator("> .irs > .irs-from")
        self.loc_irs_label_to = self.loc_irs.locator("> .irs > .irs-to")

    def expect_value(
        self,
        value: typing.Tuple[PatternOrStr, PatternOrStr]
        | typing.Tuple[PatternOrStr, MISSING_TYPE]
        | typing.Tuple[MISSING_TYPE, PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
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
        value: typing.Tuple[str, str]
        | typing.Tuple[str, MISSING_TYPE]
        | typing.Tuple[MISSING_TYPE, str],
        *,
        max_err_values: int = 15,
        timeout: Timeout = None,
    ) -> None:
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
    _InputWithLabel,
):
    # id: str,
    # label: TagChild,
    # value: Optional[Union[date, str]] = None,
    # min: Optional[Union[date, str]] = None,
    # max: Optional[Union[date, str]] = None,
    # format: str = "yyyy-mm-dd",
    # startview: str = "month",
    # weekstart: int = 0,
    # language: str = "en",
    # width: Optional[str] = None,
    # autoclose: bool = True,
    # datesdisabled: Optional[list[str]] = None,
    # daysofweekdisabled: Optional[list[int]] = None,

    # Due to the `language` parameter, we can't use `datetime.date` as a value type

    def expect_value(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
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
        expect_attr(self.loc, "data-min-date", value=value, timeout=timeout)

    def expect_max_date(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "data-max-date", value=value, timeout=timeout)

    def expect_format(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "data-date-format", value=value, timeout=timeout)

    def expect_startview(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "data-date-start-view", value=value, timeout=timeout)

    def expect_weekstart(
        self,
        value: int | AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        if isinstance(value, int):
            value = str(value)
        expect_attr(self.loc, "data-date-week-start", value=value, timeout=timeout)

    def expect_language(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "data-date-language", value=value, timeout=timeout)

    # autoclose: bool = True,
    def expect_autoclose(
        self,
        value: Literal["true", "false"],
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "data-date-autoclose", value=value, timeout=timeout)

    def expect_datesdisabled(
        self,
        value: list[str] | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        if isinstance(value, list):
            assert len(value) > 0, "`value` must be `None` or a non-empty list"
        value_str = "null" if value is None else json.dumps(value)
        expect_attr(
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
        if isinstance(value, list):
            assert len(value) > 0, "`value` must be `None` or a non-empty list"
        value_str = "null" if value is None else json.dumps(value)
        expect_attr(
            self.loc,
            "data-date-days-of-week-disabled",
            value=value_str,
            timeout=timeout,
        )


class InputDate(_DateBase):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc="input[type=text].form-control",
            loc_container=f"div#{id}.shiny-input-container",
        )


class InputDateRange(_WidthContainerM, _InputWithLabel):
    # id: str,
    # label: TagChild,
    # *,
    # start: Optional[Union[date, str]] = None,
    # end: Optional[Union[date, str]] = None,
    # min: Optional[Union[date, str]] = None,
    # max: Optional[Union[date, str]] = None,
    # format: str = "yyyy-mm-dd",
    # startview: str = "month",
    # weekstart: int = 0,
    # language: str = "en",
    # separator: str = " to ",
    # width: Optional[str] = None,
    # autoclose: bool = True,

    loc_separator: Locator
    loc_start: Locator
    loc_end: Locator
    date_start: _DateBase
    date_end: _DateBase

    def __init__(self, page: Page, id: str) -> None:
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
        start = value[0]
        end = value[1]
        # TODO-future; Composable set() methods?
        if start is not None:
            self.date_start.set(value=start, timeout=timeout)
        if end is not None:
            self.date_end.set(value=end, timeout=timeout)

    def expect_value(
        self,
        value: typing.Tuple[PatternOrStr, PatternOrStr]
        | typing.Tuple[PatternOrStr, MISSING_TYPE]
        | typing.Tuple[MISSING_TYPE, PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
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
        playwright_expect(self.loc_separator).to_have_text(value, timeout=timeout)

    # width: Optional[str] = None,

    # autoclose: bool = True,
    def expect_autoclose(
        self,
        value: Literal["true", "false"],
        *,
        timeout: Timeout = None,
    ) -> None:
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
    id: str
    loc: Locator
    page: Page

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
        """Note this function will trim value and output text value before comparing them"""
        self.expect.to_have_text(value, timeout=timeout)


class _OutputContainerP(_OutputBaseP, Protocol):
    def expect_container_tag(
        self: _OutputBaseP,
        tag_name: Literal["span", "div"] | str,
        *,
        timeout: Timeout = None,
    ) -> None:
        ...


class _OutputContainerM:
    def expect_container_tag(
        self: _OutputBaseP,
        tag_name: Literal["span", "div"] | str,
        *,
        timeout: Timeout = None,
    ) -> None:
        loc = self.loc.locator(f"xpath=self::{tag_name}")
        playwright_expect(loc).to_have_count(1, timeout=timeout)


class _OutputInlineContainerM(_OutputContainerM):
    def expect_inline(
        self: _OutputContainerP, inline: bool = False, *, timeout: Timeout = None
    ) -> None:
        tag_name = "span" if inline else "div"
        self.expect_container_tag(tag_name, timeout=timeout)


class OutputText(_OutputInlineContainerM, _OutputTextValue):
    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        super().__init__(page, id=id, loc=f"#{id}.shiny-text-output")


# TODO-Karan: Add OutputCode class
class OutputTextVerbatim(_OutputTextValue):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(page, id=id, loc=f"pre#{id}.shiny-text-output")

    def expect_has_placeholder(
        self, placeholder: bool = False, *, timeout: Timeout = None
    ) -> None:
        _expect_class_value(
            self.loc,
            cls="noplaceholder",
            has_class=not placeholder,
            timeout=timeout,
        )


class _OutputImageBase(_OutputInlineContainerM, _OutputBase):
    # id: str
    # width: str = "100%"
    # height: str = "400px"
    # inline: bool = False

    loc_img: Locator

    def __init__(self, page: Page, id: str, loc_classes: str = "") -> None:
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
        expect_to_have_style(self.loc, "height", value, timeout=timeout)

    def expect_width(
        self,
        value: StyleValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_to_have_style(self.loc, "width", value, timeout=timeout)

    def expect_img_src(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc_img, "src", value, timeout=timeout)

    def expect_img_width(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc_img, "width", value, timeout=timeout)

    def expect_img_height(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc_img, "height", value, timeout=timeout)

    def expect_img_alt(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc_img, "alt", value, timeout=timeout)

    # def expect_img_style(
    #     self,
    #     value: AttrValue,
    #     *,
    #     timeout: Timeout = None,
    # ) -> None:
    #     expect_attr(self.loc_img, "style", value, timeout=timeout)


class OutputImage(_OutputImageBase):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(page, id=id)


class OutputPlot(_OutputImageBase):
    # shiny-plot-output
    # id: str
    # width: str = "100%"
    # height: str = "400px"
    # inline: bool = False
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(page, id=id, loc_classes=".shiny-plot-output")


class OutputUi(_OutputInlineContainerM, _OutputBase):
    # id: str,
    # inline: bool = False,
    # container: Optional[TagFunction] = None,
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(page, id=id, loc=f"#{id}")

    # TODO-future; Should we try verify that `recalculating` class is not present? Do this for all outputs!
    def expect_empty(self, empty: bool, *, timeout: Timeout = None) -> None:
        if empty:
            self.expect.to_be_empty(timeout=timeout)
        else:
            self.expect.not_to_be_empty(timeout=timeout)

    def expect_text(self, text: str, *, timeout: Timeout = None) -> None:
        self.expect.to_have_text(text, timeout=timeout)


# When making selectors, use `xpath` so that direct decendents can be checked
class OutputTable(_OutputBase):
    # id: str,
    # **kwargs: TagAttrArg
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(page, id=id, loc=f"#{id}")

    def expect_cell(
        self,
        text: PatternOrStr,
        row: int,
        col: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        assert_type(row, int)
        assert_type(col, int)
        playwright_expect(
            self.loc.locator(
                f"xpath=./table/tbody/tr[{row}]/td[{col}] | ./table/tbody/tr[{row}]/th[{col}]"
            )
        ).to_have_text(text, timeout=timeout)

    def expect_column_labels(
        self,
        labels: ListPatternOrStr | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        if isinstance(labels, list) and len(labels) == 0:
            labels = None

        if labels is None:
            playwright_expect(
                self.loc.locator("xpath=./table/thead/tr/th")
            ).to_have_count(0, timeout=timeout)
        else:
            playwright_expect(
                self.loc.locator("xpath=./table/thead/tr/th")
            ).to_have_text(labels, timeout=timeout)

    def expect_column_text(
        self,
        col: int,
        # Can't use `None` as we don't know how many rows exist
        text: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        assert_type(col, int)
        playwright_expect(
            self.loc.locator(f"xpath=./table/tbody/tr/td[{col}]")
        ).to_have_text(
            text,
            timeout=timeout,
        )

    def expect_n_col(
        self,
        n: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        playwright_expect(
            # self.loc.locator("xpath=./table/thead/tr[1]/(td|th)")
            self.loc.locator("xpath=./table/thead/tr[1]/td | ./table/thead/tr[1]/th")
        ).to_have_count(
            n,
            timeout=timeout,
        )

    def expect_n_row(
        self,
        n: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        playwright_expect(self.loc.locator("xpath=./table/tbody/tr")).to_have_count(
            n,
            timeout=timeout,
        )


class Sidebar(
    _WidthLocM,
    _InputWithContainer,
):
    # *args: TagChild | TagAttrs,
    # width: CssUnit = 250,
    # position: Literal["left", "right"] = "left",
    # open: Literal["desktop", "open", "closed", "always"] = "desktop",
    # id: Optional[str] = None,
    # title: TagChild | str = None,
    # bg: Optional[str] = None,
    # fg: Optional[str] = None,
    # class_: Optional[str] = None,  # TODO-future; Consider using `**kwargs` instead
    # max_height_mobile: Optional[str | float] = None,
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"> aside#{id}",
            loc_container="div.bslib-sidebar-layout",
        )
        self.loc_handle = self.loc_container.locator("button.collapse-toggle")
        self.loc_position = self.loc.locator("..")

    def expect_text(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        playwright_expect(self.loc).to_have_text(value, timeout=timeout)

    def expect_position(
        self, position: Literal["left", "right"], *, timeout: Timeout = None
    ) -> None:
        is_right_sidebar = position == "right"
        _expect_class_value(
            self.loc_position,
            f"sidebar-{position}",
            is_right_sidebar,
            timeout=timeout,
        )

    def expect_handle(self, exists: bool, *, timeout: Timeout = None) -> None:
        playwright_expect(self.loc_handle).to_have_count(int(exists), timeout=timeout)

    def expect_open(self, open: bool, *, timeout: Timeout = None) -> None:
        playwright_expect(self.loc_handle).to_have_attribute(
            "aria-expanded", str(open).lower(), timeout=timeout
        )

    def set(self, open: bool, *, timeout: Timeout = None) -> None:
        if open ^ (self.loc_handle.get_attribute("aria-expanded") == "true"):
            self.toggle(timeout=timeout)

    def toggle(self, *, timeout: Timeout = None) -> None:
        self.loc_handle.wait_for(state="visible", timeout=timeout)
        self.loc_handle.scroll_into_view_if_needed(timeout=timeout)
        self.loc_handle.click(timeout=timeout)


class _CardBodyP(_InputBaseP, Protocol):
    loc_body: Locator


class _CardBodyM:
    def expect_body(
        self: _CardBodyP,
        text: PatternOrStr | list[PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
        """Note: If testing against multiple elements, text should be an array"""
        playwright_expect(self.loc).to_have_text(
            text,
            timeout=timeout,
        )


class _CardFooterLayoutP(_InputBaseP, Protocol):
    loc_footer: Locator


class _CardFooterM:
    def expect_footer(
        self: _CardFooterLayoutP,
        text: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        playwright_expect(self.loc_footer).to_have_text(
            text,
            timeout=timeout,
        )


class _CardFullScreenLayoutP(_OutputBaseP, Protocol):
    loc_title: Locator
    _loc_fullscreen: Locator
    _loc_close_button: Locator


class _CardFullScreenM:
    def open_full_screen(
        self: _CardFullScreenLayoutP, *, timeout: Timeout = None
    ) -> None:
        self.loc_title.hover(timeout=timeout)
        self._loc_fullscreen.wait_for(state="visible", timeout=timeout)
        self._loc_fullscreen.click(timeout=timeout)

    def close_full_screen(
        self: _CardFullScreenLayoutP, *, timeout: Timeout = None
    ) -> None:
        self._loc_close_button.click(timeout=timeout)

    def expect_full_screen(
        self: _CardFullScreenLayoutP, open: bool, *, timeout: Timeout = None
    ) -> None:
        playwright_expect(self._loc_close_button).to_have_count(
            int(open), timeout=timeout
        )


class ValueBox(
    _WidthLocM,
    _CardFullScreenM,
    _InputWithContainer,
):
    # title: TagChild,
    # value: TagChild,
    # *args: TagChild | TagAttrs,
    # showcase: TagChild = None,
    # showcase_layout: ((TagChild, Tag) -> CardItem) | None = None,
    # full_screen: bool = False,
    # theme_color: str | None = "primary",
    # height: CssUnit | None = None,
    # max_height: CssUnit | None = None,
    # fill: bool = True,
    # class_: str | None = None,
    # **kwargs: TagAttrValue
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc_container=f"div#{id}.bslib-value-box",
            loc="> div > .value-box-grid",
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
        expect_to_have_style(self.loc_container, "height", value, timeout=timeout)

    def expect_title(
        self,
        text: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        playwright_expect(self.loc_title).to_have_text(
            text,
            timeout=timeout,
        )

    def expect_value(
        self,
        text: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        playwright_expect(self.loc).to_have_text(
            text,
            timeout=timeout,
        )

    def expect_body(
        self,
        text: PatternOrStr | list[PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
        """Note: If testing against multiple elements, text should be an array"""
        playwright_expect(self.loc_body).to_have_text(
            text,
            timeout=timeout,
        )

    # hard to test since it can be customized by user
    # def expect_showcase_layout(self, layout, *, timeout: Timeout = None) -> None:
    #     raise NotImplementedError()


class Card(_WidthLocM, _CardFooterM, _CardBodyM, _CardFullScreenM, _InputWithContainer):
    # *args: TagChild | TagAttrs | CardItem,
    # full_screen: bool = False,
    # height: CssUnit | None = None,
    # max_height: CssUnit | None = None,
    # min_height: CssUnit | None = None,
    # fill: bool = True,
    # class_: str | None = None,
    # wrapper: WrapperCallable | MISSING_TYPE | None = MISSING,
    # **kwargs: TagAttrValue
    def __init__(self, page: Page, id: str) -> None:
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
        text: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        playwright_expect(self.loc_title).to_have_text(
            text,
            timeout=timeout,
        )

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

    def expect_max_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        expect_to_have_style(self.loc_container, "max-height", value, timeout=timeout)

    def expect_min_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        expect_to_have_style(self.loc_container, "min-height", value, timeout=timeout)

    def expect_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        expect_to_have_style(self.loc_container, "height", value, timeout=timeout)


# Experimental below


class Accordion(
    _WidthLocM,
    _InputWithContainer,
):
    # *args: AccordionPanel | TagAttrs,
    # id: Optional[str] = None,
    # open: Optional[bool | str | list[str]] = None,
    # multiple: bool = True,
    # class_: Optional[str] = None,
    # width: Optional[CssUnit] = None,
    # height: Optional[CssUnit] = None,
    # **kwargs: TagAttrValue,
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc="> div.accordion-item",
            loc_container=f"div#{id}.accordion.shiny-bound-input",
        )
        self.loc_open = self.loc.locator(
            # Return self
            "xpath=.",
            # Simple approach as position is not needed
            has=page.locator(
                "> div.accordion-collapse.show",
            ),
        )

    def expect_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        expect_to_have_style(self.loc_container, "height", value, timeout=timeout)

    def expect_width(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        expect_to_have_style(self.loc_container, "width", value, timeout=timeout)

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
        selected: str | list[str],
        *,
        timeout: Timeout = None,
    ) -> None:
        if isinstance(selected, str):
            selected = [selected]
        for element in self.loc.element_handles():
            element.wait_for_element_state(state="visible", timeout=timeout)
            element.scroll_into_view_if_needed(timeout=timeout)
            elem_value = element.get_attribute("data-value")
            if elem_value is None:
                raise ValueError(
                    "Accordion panel does not have a `data-value` attribute"
                )
            self.accordion_panel(elem_value).set(
                elem_value in selected, timeout=timeout
            )

    def accordion_panel(
        self,
        data_value: str,
    ) -> AccordionPanel:
        return AccordionPanel(self.page, self.id, data_value)


class AccordionPanel(
    _WidthLocM,
    _InputWithContainer,
):
    #    self,
    #     *args: TagChild | TagAttrs,
    #     data_value: str,
    #     icon: TagChild | None,
    #     title: TagChild | None,
    #     id: str | None,
    #     **kwargs: TagAttrValue,
    def __init__(self, page: Page, id: str, data_value: str) -> None:
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
        self.loc_body_visible = self.loc.locator("> .accordion-collapse.show")

    def expect_label(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        playwright_expect(self.loc_label).to_have_text(value, timeout=timeout)

    def expect_body(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        playwright_expect(self.loc_body).to_have_text(value, timeout=timeout)

    def expect_icon(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        playwright_expect(self.loc_icon).to_have_text(value, timeout=timeout)

    def expect_open(self, is_open: bool, *, timeout: Timeout = None) -> None:
        _expect_class_value(self.loc_body, "show", is_open, timeout=timeout)

    # user sends value of Open: true | false
    def set(self, open: bool, *, timeout: Timeout = None) -> None:
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        expect_not_to_have_class(self.loc_body, "collapsing", timeout=timeout)
        if self.loc_body_visible.count() != int(open):
            self.toggle(timeout=timeout)

    def toggle(self, *, timeout: Timeout = None) -> None:
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        self.loc_header.click(timeout=timeout)


class _OverlayBase(_InputBase):
    def __init__(
        self,
        page: Page,
        *,
        id: str,
        loc: InitLocator,
        overlay_name: str,
        overlay_selector: str,
    ) -> None:
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

    @property
    def loc_overlay_body(self) -> Locator:
        # Can not leverage `self.loc_overlay_container` as `self._overlay_selector` must
        # be concatenated directly to the result of `self._get_overlay_id()`
        return self.page.locator(f"#{self._get_overlay_id()}{self._overlay_selector}")

    @property
    def loc_overlay_container(self) -> Locator:
        return self.page.locator(f"#{self._get_overlay_id()}")

    def expect_body(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        playwright_expect(self.loc_overlay_body).to_have_text(value, timeout=timeout)

    def expect_active(self, active: bool, *, timeout: Timeout = None) -> None:
        value = re.compile(r".*") if active else None
        return expect_attr(
            loc=self.loc_trigger,
            timeout=timeout,
            name="aria-describedby",
            value=value,
        )

    def expect_placement(self, value: str, *, timeout: Timeout = None) -> None:
        return expect_attr(
            loc=self.loc_overlay_container,
            timeout=timeout,
            name="data-popper-placement",
            value=value,
        )


class Popover(_OverlayBase):
    # trigger: TagChild,
    # *args: TagChild | TagAttrs,
    # title: Optional[TagChild] = None,
    # id: Optional[str] = None,
    # placement: Literal["auto", "top", "right", "bottom", "left"] = "auto",
    # options: Optional[dict[str, Any]] = None,
    # **kwargs: TagAttrValue,
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"bslib-popover#{id}",
            overlay_name="popover",
            overlay_selector=".popover > div.popover-body",
        )

    def set(self, open: bool, timeout: Timeout = None) -> None:
        if open ^ self.loc_overlay_body.count() > 0:
            self.toggle()

    def toggle(self, timeout: Timeout = None) -> None:
        self.loc_trigger.wait_for(state="visible", timeout=timeout)
        self.loc_trigger.scroll_into_view_if_needed(timeout=timeout)
        self.loc_trigger.click(timeout=timeout)


class Tooltip(_OverlayBase):
    # trigger: TagChild,
    # *args: TagChild | TagAttrs,
    # id: Optional[str] = None,
    # placement: Literal["auto", "top", "right", "bottom", "left"] = "auto",
    # options: Optional[dict[str, object]] = None,
    # **kwargs: TagAttrValue,
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"bslib-tooltip#{id}",
            overlay_name="tooltip",
            overlay_selector=".tooltip > div.tooltip-inner",
        )

    def set(self, open: bool, timeout: Timeout = None) -> None:
        if open ^ self.loc_overlay_body.count() > 0:
            self.toggle(timeout=timeout)
        if not open:
            self.loc_overlay_body.click()

    def toggle(self, timeout: Timeout = None) -> None:
        self.loc_trigger.wait_for(state="visible", timeout=timeout)
        self.loc_trigger.scroll_into_view_if_needed(timeout=timeout)
        self.loc_trigger.hover(timeout=timeout)


class _LayoutNavItemBase(_InputWithContainer):
    def nav_item(
        self,
        value: str,
    ) -> LayoutNavItem:
        return LayoutNavItem(self.page, self.id, value)

    def set(self, value: str, *, timeout: Timeout = None) -> None:
        self.nav_item(value).click(timeout=timeout)

    def expect_value(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        # data attribute of active tab and compare with value
        playwright_expect(
            self.loc_container.locator('a[role="tab"].active')
        ).to_have_attribute("data-value", value, timeout=timeout)

    # TODO-future: Make it a single locator expectation
    # get active content instead of assertion
    @property
    def loc_active_content(self) -> Locator:
        datatab_id = self.loc_container.get_attribute("data-tabsetid")
        return self.page.locator(
            f"div.tab-content[data-tabsetid='{datatab_id}'] > div.tab-pane.active"
        )

    def expect_content(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        playwright_expect(self.loc_active_content).to_have_text(value, timeout=timeout)

    def expect_nav_values(
        self,
        value: list[PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
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
        self.expect.to_have_text(value, timeout=timeout)


class LayoutNavItem(_InputWithContainer):
    # *args: NavSetArg,
    # id: Optional[str] = None,
    # selected: Optional[str] = None,
    # header: TagChild = None,
    # footer: TagChild = None,
    def __init__(self, page: Page, id: str, data_value: str) -> None:
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
        """Note. This requires 2 steps. Will not work if the overlay element is rapidly created during locator fetch"""
        datatab_id = self.loc_container.get_attribute("data-tabsetid")
        return self.page.locator(
            f"div.tab-content[data-tabsetid='{datatab_id}'] > div.tab-pane[data-value='{self._data_value}']"
        )

    def click(self, *, timeout: Timeout = None) -> None:
        self.loc.click(timeout=timeout)

    def expect_active(self, active: bool, *, timeout: Timeout = None) -> None:
        _expect_class_value(self.loc, "active", active, timeout=timeout)

    def expect_content(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        playwright_expect(self.loc_content).to_have_text(value, timeout=timeout)


class LayoutNavsetTab(_LayoutNavItemBase):
    # *args: NavSetArg,
    # id: Optional[str] = None,
    # selected: Optional[str] = None,
    # header: TagChild = None,
    # footer: TagChild = None,
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc_container=f"ul#{id}.nav-tabs",
            loc="a[role='tab']",
        )


class LayoutNavSetPill(_LayoutNavItemBase):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc_container=f"ul#{id}.nav-pills",
            loc="> li.nav-item",
        )


class LayoutNavSetUnderline(_LayoutNavItemBase):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc_container=f"ul#{id}.nav-underline",
            loc="> li.nav-item",
        )


class LayoutNavSetPillList(_LayoutNavItemBase):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc_container=f"ul#{id}.nav-stacked",
            loc="> li.nav-item",
        )


class LayoutNavSetCardTab(_LayoutNavItemBase):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc_container=f".bslib-card > div > ul#{id}.nav-tabs",
            loc="> li.nav-item",
        )


class LayoutNavSetCardPill(_LayoutNavItemBase):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc_container=f".bslib-card > div > ul#{id}.nav-pills",
            loc="> li.nav-item",
        )


class LayoutNavSetCardUnderline(_LayoutNavItemBase):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc_container=f".bslib-card > div > ul#{id}.nav-underline",
            loc="> li.nav-item",
        )


class LayoutNavSetHidden(_LayoutNavItemBase):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc_container=f"ul#{id}.nav-hidden",
            loc="> li.nav-item",
        )


class LayoutNavSetBar(_LayoutNavItemBase):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc_container=f"ul#{id}.navbar-nav",
            loc="> li.nav-item",
        )


class OutputDataFrame(_InputWithContainer):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc_container=f"#{id}.html-fill-item",
            loc="> div > div.shiny-data-grid-grid",
        )
        self.loc_columns = self.loc.locator("> table > thead")
        self.loc_rows = self.loc.locator("> table > tbody")

    def expect_n_row(self, row_number: int, *, timeout: Timeout = None):
        playwright_expect(self.loc_rows.locator("> tr")).to_have_count(
            row_number, timeout=timeout
        )

    def expect_cell(
        self,
        text: PatternOrStr,
        row: int,
        col: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        assert_type(row, int)
        assert_type(col, int)
        playwright_expect(
            self.loc.locator(
                f"xpath=./table/tbody/tr[{row}]/td[{col}] | ./table/tbody/tr[{row}]/th[{col}]"
            )
        ).to_have_text(text, timeout=timeout)

    def expect_column_labels(
        self,
        labels: ListPatternOrStr | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        if isinstance(labels, list) and len(labels) == 0:
            labels = None

        if labels is None:
            playwright_expect(
                self.loc.locator("xpath=./table/thead/tr/th")
            ).to_have_count(0, timeout=timeout)
        else:
            playwright_expect(
                self.loc.locator("xpath=./table/thead/tr/th")
            ).to_have_text(labels, timeout=timeout)

    def expect_column_text(
        self,
        col: int,
        # Can't use `None` as we don't know how many rows exist
        text: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        assert_type(col, int)
        playwright_expect(
            self.loc.locator(f"xpath=./table/tbody/tr/td[{col}]")
        ).to_have_text(
            text,
            timeout=timeout,
        )

    def expect_n_col(
        self,
        n: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        playwright_expect(
            # self.loc.locator("xpath=./table/thead/tr[1]/(td|th)")
            self.loc.locator("xpath=./table/thead/tr[1]/td | ./table/thead/tr[1]/th")
        ).to_have_count(
            n,
            timeout=timeout,
        )


# TODO: Use mixin for dowloadlink and download button
class DownloadLink(_InputActionBase):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"#{id}.shiny-download-link:not(.btn)",
        )


class DownloadButton(
    _WidthLocM,
    _InputActionBase,
):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"#{id}.btn.shiny-download-link",
        )
