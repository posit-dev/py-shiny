"""Barret Facade classes for working with Shiny inputs/outputs in Playwright"""
import json
import pathlib
import re
import sys
import time

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol
else:
    from typing_extensions import Literal
    from typing_extensions import Protocol

import typing

from playwright.sync_api import FilePayload, FloatRect, Locator, Page, Position
from playwright.sync_api import expect as playwright_expect

"""
Questions:
* While `expect_*_to_have_value()` matches the setup of `expect(x).to_have_value()`, it is a bit verbose. Should we just use `expect_*()` as we only use it in a single context? (Only adding the suffix if other methods like `to_have_html()` or `to_have_text()` would make sense.)
    * Ans: Try things out
* `_DateBase` is signaled as private, but `InputDateRange` will have two fields of `date_start` and `date_end`. Due to how the init selectors are created, they are not `InputDate` instances. Should we make `_DateBase` public?
* Can Date pickers set the `value` attribute on the corresponding input element? If so, we could use `expect_value()` to check the value of the input element.
* In `test_output_table.py`, why can't I write `barret = ["1", "2"]; table.expect_column_labels(barret)`? (Typing issue)
* For set methods or expect_value methods, should we not allow `None` as a value? Ex: InputDateRange does not allow this, but InputText does (upgrades `None` to `""`)
    * Ans w/ Winston: Be strict and do not upgrade unless necessary

* Should we guard against nest shiny input objects? (Should we tighten up the selectors?). CSS selector to only select first occurance: https://stackoverflow.com/a/71749400/591574
* TODO-barret; Make sure multiple usage of `timeout` has the proper values. Should followup usages be `0` to force it to be immediate? (Is `0` the right value?)

Done:
* input_action_button
* input_action_link
* input_checkbox
* input_checkbox_group
* input_date
* input_date_range
* input_file
* input_numeric
* input_password
* input_radio_buttons
* input_select
* input_selectize
* input_slider
* input_switch
* input_text
* input_text_area
* output_image
* output_plot
* output_table
* output_text
* output_text_verbatim
* output_ui

# Class definitions
* Fields
  * Try to mirror playwright as much as possible.
  * There are no properties, only methods; This allows for timeout values to be passed through and for complex methods.
    * Locators will stay as properties
  * Don't sub-class. For now, use `_` separatation and use `loc` or `value` as a prefix
* Approach
  * Use locators / playwright_expect as much as possible
    * It should not be necessary to use `assert` directly.
    * MUST wait for `Locator`s to do their job
  * DO NOT provide `value` methods
  * Add _set_ methods only if a user would perform them

# Mixins
* Use mixins to add consistent functionality to different classes
* These classes should **never** be instantiated directly
* Use `typing.Protocol` to define the interface of what is required on `self`
* Add methods to the mixin if they are consistently used across multiple classes
  * If a method is only used in one class, it should be defined in that class
  * If a method is used inconsistently, make/use a helper method
"""

OptionalStr = typing.Optional[str]
OptionalInt = typing.Optional[int]

# TODO-barret; Add new types that are `PatternOrStr | MISSINGTYPE`

PatternOrStr = typing.Union[str, typing.Pattern[str]]
TextValue = typing.Union[PatternOrStr, None]
AttrValue = typing.Union[PatternOrStr, None]
StyleValue = typing.Union[PatternOrStr, None]


Timeout = typing.Union[float, None]
InitLocator = typing.Union[Locator, str]


def set_text(
    loc: Locator,
    text: str,
    *,
    delay: typing.Union[float, None] = None,
    timeout: Timeout = None,
) -> None:
    # TODO-future; Composable set() method
    loc.fill("", timeout=timeout)  # Reset the value
    loc.type(text, delay=delay, timeout=timeout)  # Type the value


def assert_el_has_class(loc: Locator, cls: str) -> None:
    el_cls = loc.get_attribute("class")
    if el_cls is None:
        raise AssertionError("Element has no class attribute")
    assert el_cls.index(cls) >= 0


R = typing.TypeVar("R")

# # Pylance could not find the return type of `float_attr = maybe_cast_attr_gen(float)`.
# # However, vscode could display the return type of `float_attr` correctly.
# Generic method generator to cast a non-None attribute value to a type
# def maybe_cast_attr_gen(
#     fn: typing.Callable[[typing.Any], R]
# ) -> typing.Callable[[Locator, str, Timeout], typing.Union[R, None]]:
#     def cast_attr(loc: Locator, attr_name: str, timeout: Timeout = None) -> typing.Union[R, None]:
#         ret = loc.get_attribute(attr_name, timeout=timeout)
#         if ret is not None:
#             ret = fn(ret)
#         return ret
#     return cast_attr
# float_attr = maybe_cast_attr_gen(float)
# str_attr = maybe_cast_attr_gen(str)


def maybe_cast_attr(
    fn: typing.Callable[[typing.Any], R],
    loc: Locator,
    attr_name: str,
    timeout: Timeout = None,
) -> typing.Optional[R]:
    ret = loc.get_attribute(attr_name, timeout=timeout)
    if ret is not None:
        ret = fn(ret)
    return ret


def float_attr(
    loc: Locator, attr_name: str, timeout: Timeout = None
) -> typing.Optional[float]:
    return maybe_cast_attr(fn=float, loc=loc, attr_name=attr_name, timeout=timeout)


def str_attr(
    loc: Locator, attr_name: str, timeout: Timeout = None
) -> typing.Optional[str]:
    return maybe_cast_attr(fn=str, loc=loc, attr_name=attr_name, timeout=timeout)


def int_attr(loc: Locator, attr_name: str, timeout: Timeout = None) -> OptionalInt:
    return maybe_cast_attr(fn=int, loc=loc, attr_name=attr_name, timeout=timeout)


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


def expect_class_value(
    loc: Locator,
    cls: str,
    has_class: bool,
    timeout: Timeout = None,
) -> None:
    """Expect a locator to have (or not to have) a class value"""
    cls_regex = re.compile(rf"\b{cls}\b")
    if has_class:
        playwright_expect(loc).to_have_class(cls_regex, timeout=timeout)
    else:
        playwright_expect(loc).not_to_have_class(cls_regex, timeout=timeout)


def get_el_style(
    loc: Locator,
    css_key: str,
    timeout: Timeout = None,
) -> typing.Optional[str]:
    ret = loc.get_attribute("style", timeout=timeout) or ""
    m = re.search(css_key + r":\s*([^\s;]+)", ret)
    if m:
        # Return match
        return m.group(1)
    return None


def expect_el_style(
    loc: Locator,
    css_key: str,
    # Str representation for value. Will be put in a regex with `css_key`
    css_value: StyleValue,
    timeout: Timeout = None,
) -> None:
    """Expect a style to have a value. If `value` is `None`, then the style should not exist."""
    if css_value is None:
        # Not allowed to have any value for the style
        playwright_expect(loc).not_to_have_attribute(
            "style", re.compile(f"{css_key}\\s*:"), timeout=timeout
        )
        return

    if isinstance(css_value, str):
        css_value = re.compile(css_value)

    playwright_expect(loc).to_have_attribute(
        "style", re.compile(f"{css_key}\\s*:\\s*{css_value.pattern}"), timeout=timeout
    )


def expect_multiple(loc: Locator, multiple: bool, timeout: Timeout = None) -> None:
    ex_multiple = playwright_expect(loc)
    if multiple:
        ex_multiple.to_have_attribute("multiple", "True", timeout=timeout)
    else:
        ex_multiple.not_to_have_attribute(
            "multiple", re.compile(r".*"), timeout=timeout
        )


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
        loc_label: InitLocator = "label",
    ) -> None:
        super().__init__(
            page,
            id=id,
            loc_container=loc_container,
            loc=loc,
        )

        if isinstance(loc_label, str):
            loc_label = self.loc_container.locator(loc_label)
        self.loc_label = loc_label

    def expect_label_to_have_text(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        playwright_expect(self.loc_label).to_have_text(value, timeout=timeout)


class _WidthLocM:
    def expect_width_to_have_value(
        self: _InputBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "width", value=value, timeout=timeout)


class _WidthContainerM:
    def expect_width_to_have_value(
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
        value: TextValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        if value is None:
            value = ""
        playwright_expect(self.loc).to_have_value(value, timeout=timeout)


class InputNumeric(
    _SetTextM,
    _ExpectTextInputValueM,
    _WidthLocM,
    _InputWithLabel,
):
    # id: str,
    # label: TagChildArg,
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

    def expect_min_to_have_value(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "min", value=value, timeout=timeout)

    def expect_max_to_have_value(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "max", value=value, timeout=timeout)

    def expect_step_to_have_value(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "step", value=value, timeout=timeout)


class _ExpectSpellcheckAttrM:
    def expect_spellcheck_to_have_value(
        self: _InputBaseP,
        value: typing.Union[Literal["true", "false"], None],
        *,
        timeout: Timeout = None,
    ) -> None:
        # self.spellcheck.expect_to_have_value(value, timeout=timeout)
        expect_attr(self.loc, "spellcheck", value=value, timeout=timeout)


class _ExpectPlaceholderAttrM:
    def expect_placeholder_to_have_value(
        self: _InputBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "placeholder", value=value, timeout=timeout)


class _ExpectAutocompleteAttrM:
    def expect_autocomplete_to_have_value(
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
    # label: TagChildArg,
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
    # label: TagChildArg,
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

    def get_width(self, *, timeout: Timeout = None) -> typing.Optional[str]:
        return get_el_style(self.loc_container, "width", timeout=timeout)

    # This class does not inherit from `_WidthContainerM`
    # as the width is in the element style
    def expect_width_to_have_value(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_el_style(self.loc_container, "width", value, timeout=timeout)


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
    # label: TagChildArg,
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

    def expect_width_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        if value is None:
            expect_el_style(self.loc_container, "width", None, timeout=timeout)
            expect_el_style(self.loc, "width", "100%", timeout=timeout)
        else:
            expect_el_style(self.loc_container, "width", value, timeout=timeout)
            expect_el_style(self.loc, "width", None, timeout=timeout)

    def expect_height_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_el_style(self.loc, "height", value, timeout=timeout)

    def expect_cols_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_attr(self.loc, "cols", value=value, timeout=timeout)

    def expect_rows_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_attr(self.loc, "rows", value=value, timeout=timeout)

    def expect_resize_to_have_value(
        self,
        value: typing.Union[Resize, None],
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "resize", value=value, timeout=timeout)


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
            loc_label=f"label[for='{id}']",
        )
        self.loc_selected = self.loc.locator("option:checked")
        self.loc_choices = self.loc.locator("option")
        self.loc_choice_groups = self.loc.locator("optgroup")

    def set(
        self,
        selected: typing.Union[str, typing.List[str]],
        *,
        timeout: Timeout = None,
    ) -> None:
        if isinstance(selected, str):
            selected = [selected]
        self.loc.select_option(value=selected, timeout=timeout)

    def expect_choices(
        self,
        # TODO-barret; support patterns?
        choices: typing.Union[typing.List[str], None],
        *,
        timeout: Timeout = None,
    ) -> None:
        """Expect choices to be in order"""
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if choices is not None and len(choices) == 0:
            choices = None
        if choices is None:
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
        selected: typing.Union[typing.List[PatternOrStr], PatternOrStr, None],
        *,
        timeout: Timeout = None,
    ) -> None:
        """Expect choices to be in order"""
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if isinstance(selected, list) and len(selected) == 0:
            selected = None
        if selected is None:
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
        choice_groups: typing.Union[
            # TODO-barret; support patterns?
            typing.List[str],
            None,
        ],
        *,
        timeout: Timeout = None,
    ) -> None:
        """Expect choices to be in order"""
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if choice_groups is not None and len(choice_groups) == 0:
            choice_groups = None
        if choice_groups is None:
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
        choice_labels: typing.Union[typing.List[PatternOrStr], None],
        *,
        timeout: Timeout = None,
    ) -> None:
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if choice_labels is not None and len(choice_labels) == 0:
            choice_labels = None
        if choice_labels is None:
            playwright_expect(self.loc_choices).to_have_count(0, timeout=timeout)
            return
        playwright_expect(self.loc_choices).to_have_text(choice_labels, timeout=timeout)

    # multiple: bool = False,
    def expect_multiple(self, multiple: bool, *, timeout: Timeout = None) -> None:
        expect_multiple(self.loc, multiple, timeout=timeout)

    def expect_size_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_attr(
            self.loc,
            "size",
            value=value,
            timeout=timeout,
        )


class InputSelect(_InputSelectBase):
    # id: str,
    # label: TagChildArg,
    # choices: SelectChoicesArg,
    # selected: Optional[Union[str, List[str]]] = None,
    # multiple: bool = False,
    # selectize: bool = False,
    # width: Optional[str] = None,
    # size: Optional[str] = None,
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(
            page,
            id=id,
            select_class="",
        )

    # selectize: bool = False,
    def expect_selectize(self, selectize: bool, *, timeout: Timeout = None) -> None:
        # class_=None if selectize else "form-select",
        expect_class_value(
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
            select_class=".form-select",
        )


class _InputActionBase(_InputBase):
    # TODO-barret; Should these label methods be different?
    def expect_label_to_have_text(
        self,
        value: TextValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """Must include icon if present"""

        if value is None:
            value = ""
        self.expect.to_have_text(value, timeout=timeout)

    def click(self, *, timeout: Timeout = None, **kwargs: typing.Any) -> None:
        self.loc.click(timeout=timeout, **kwargs)


class InputActionButton(
    _WidthLocM,
    _InputActionBase,
):
    # label: TagChildArg,
    # icon: TagChildArg = None,
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
    # label: TagChildArg,
    # icon: TagChildArg = None,

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


class InputCheckboxBase(
    _WidthContainerM,
    _InputWithLabel,
):
    # label: TagChildArg
    # value: bool = False
    # width: Optional[str] = None
    def __init__(self, page: Page, id: str, loc: InitLocator) -> None:
        super().__init__(
            page,
            id=id,
            loc=loc,
        )

    def set(
        self, value: bool, *, timeout: Timeout = None, **kwargs: typing.Any
    ) -> None:
        self.loc.set_checked(value, timeout=timeout, **kwargs)

    def toggle(self, *, timeout: Timeout = None, **kwargs: typing.Any) -> None:
        self.loc.click(timeout=timeout, **kwargs)

    def expect_to_be_checked(self, value: bool, *, timeout: Timeout = None) -> None:
        if value:
            self.expect.to_be_checked(timeout=timeout)
        else:
            self.expect.not_to_be_checked(timeout=timeout)


class InputCheckbox(InputCheckboxBase):
    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"div.checkbox > label > input#{id}[type=checkbox].shiny-bound-input",
        )


class InputSwitch(InputCheckboxBase):
    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        super().__init__(
            page,
            id=id,
            loc=f"div.form-switch > input#{id}[type=checkbox].shiny-bound-input",
        )


class _MultipleDomItems:
    @staticmethod
    def assert_arr_is_unique(arr: typing.List[str], msg: str) -> None:
        assert len(arr) == len(list(dict.fromkeys(arr))), msg

    @staticmethod
    def checked_css_str(
        is_checked: typing.Union[bool, None],
    ) -> str:
        if is_checked is None:
            return ""
        elif is_checked:
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
        # TODO-barret; support patterns?
        arr: typing.List[str],
        is_checked: typing.Optional[bool] = None,
        timeout: Timeout = None,
        key: str = "value",
    ) -> None:
        # Make sure the locator contains all of `arr`

        # Make sure the locator has len(uniq_arr) input elements
        _MultipleDomItems.assert_arr_is_unique(arr, f"`{arr_name}` must be unique")
        is_checked_str = _MultipleDomItems.checked_css_str(is_checked)

        # If there are no items, then we should not have any elements
        if len(arr) == 0:
            playwright_expect(
                loc_container.locator(f"{el_type}{is_checked_str}")
            ).to_have_count(0, timeout=timeout)
            return

        # Find all items in set
        for item in arr:
            # Given the container, make sure it contains this locator
            loc_container = loc_container.locator(
                # Return self
                "xpath=.",
                # Simple approach as position is not needed
                has=page.locator(
                    f"{el_type}[{key}='{item}']{is_checked_str}",
                ),
            )

        # If we are only looking to see if *some* (not *these only*) elements exist,
        # then we only need to check if the container locator (which must contain the elements) can be found
        playwright_expect(loc_container).to_have_count(1, timeout=timeout)

    @staticmethod
    def expect_locator_values_in_list(
        *,
        page: Page,
        loc_container: Locator,
        el_type: str,
        arr_name: str,
        # TODO-barret; support patterns?
        arr: typing.List[str],
        is_checked: typing.Optional[bool] = None,
        timeout: Timeout = None,
        key: str = "value",
    ) -> None:
        # Make sure the locator has exactly `arr` values

        # Make sure the locator has len(uniq_arr) input elements
        _MultipleDomItems.assert_arr_is_unique(arr, f"`{arr_name}` must be unique")
        is_checked_str = _MultipleDomItems.checked_css_str(is_checked)

        # If there are no items, then we should not have any elements
        if len(arr) == 0:
            playwright_expect(
                loc_container.locator(f"{el_type}{is_checked_str}")
            ).to_have_count(0, timeout=timeout)
            return

        # Find all items in set
        for item, i in zip(arr, range(len(arr))):
            # Get all elements of type
            has_locator = page.locator(f"{el_type}{is_checked_str}")
            # Get the `n`th matching element
            has_locator = has_locator.nth(i)
            # Make sure that element has the correct attribute value
            has_locator = has_locator.locator(f'xpath=self::*[@{key}="{item}"]')

            # Given the container, make sure it contains this locator
            loc_container = loc_container.locator(
                # Return self
                "xpath=.",
                has=has_locator,
            )

        # Make sure other items are not in set
        # If we know all elements are contained in the container,
        # and all elements all unique, then it should have a count of `len(arr)`
        loc_inputs = loc_container.locator(f"{el_type}{is_checked_str}")
        playwright_expect(loc_inputs).to_have_count(len(arr), timeout=timeout)


class _RadioButtonCheckboxGroupBase(_InputWithLabel):
    loc_choice_labels: Locator

    def expect_choice_labels(
        self,
        labels: typing.Union[PatternOrStr, typing.List[PatternOrStr]],
        *,
        timeout: Timeout = None,
    ) -> None:
        playwright_expect(self.loc_choice_labels).to_have_text(
            labels,
            timeout=timeout,
        )

    def expect_inline(self, inline: bool, *, timeout: Timeout = None) -> None:
        expect_class_value(
            self.loc_container,
            "shiny-input-container-inline",
            has_class=inline,
            timeout=timeout,
        )


class InputCheckboxGroup(
    _WidthContainerM,
    _RadioButtonCheckboxGroupBase,
):
    # label: TagChildArg,
    # choices: ChoicesArg,
    # selected: Optional[Union[str, List[str]]] = None,
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
            loc_label=f"label#{id}-label",
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
        selected: typing.Union[str, typing.List[str]],
        *,
        timeout: Timeout = None,
        **kwargs: typing.Any,
    ) -> None:
        if isinstance(selected, str):
            selected = [selected]

        assert len(selected) > 0, "Must select at least one item"

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

        # Could do with multiple locator calls,
        # but unchecking the elements that are not in `selected` is not possible
        # as `set_checked()` likes a single element.
        for checkbox in self.loc_choices.element_handles():
            checkbox_value = checkbox.input_value(timeout=timeout)
            checkbox.set_checked(checkbox_value in selected, timeout=timeout, **kwargs)

    def expect_choices(
        self,
        # TODO-barret; support patterns?
        choices: typing.List[str],
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
        # TODO-barret; support patterns?
        selected: typing.Union[typing.List[str], None],
        *,
        timeout: Timeout = None,
    ) -> None:
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if selected is not None and len(selected) == 0:
            selected = None
        if selected is None:
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
    # label: TagChildArg,
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
            loc_label=f"label#{id}-label",
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
        **kwargs: typing.Any,
    ) -> None:
        # Only need to set.
        # The Browser will _unset_ the previously selected radio button
        self.loc_container.locator(
            f"label input[type=radio][value='{selected}']"
        ).check(timeout=timeout)

    def expect_choices(
        self,
        # TODO-barret; support patterns?
        choices: typing.List[str],
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
        selected: TextValue,
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
    # label: TagChildArg,
    # *,
    # multiple: bool = False,
    # accept: Optional[Union[str, List[str]]] = None,
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
            loc_label=f"label[id={id}-label]",
        )
        self.loc_button = self.loc_container.locator("label span.btn")
        self.loc_file_display = self.loc_container.locator("input[type=text]")
        self.loc_progress = self.loc_container.locator(".progress-bar")

    def set(
        self,
        file_path: typing.Union[
            str,
            pathlib.Path,
            FilePayload,
            typing.List[typing.Union[str, pathlib.Path]],
            typing.List[FilePayload],
        ],
        *,
        timeout: Timeout = None,
        expect_complete_timeout: Timeout = 30 * 1000,
    ) -> None:
        self.loc.set_input_files(file_path, timeout=timeout)
        if expect_complete_timeout is not None:
            self.expect_complete(timeout=expect_complete_timeout)

    # TODO-barret: Let's make sure that if the upload errors out, expect_complete() fails.
    def expect_complete(
        self,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_el_style(self.loc_progress, "width", "100%", timeout=timeout)

    # TODO-barret; Test multiple file upload
    def expect_multiple(self, multiple: bool, *, timeout: Timeout = None) -> None:
        expect_multiple(self.loc, multiple, timeout=timeout)

    def expect_accept(
        self,
        accept: typing.Union[typing.List[str], AttrValue],
        *,
        timeout: Timeout = None,
    ) -> None:
        if isinstance(accept, typing.List):
            accept = ",".join(accept)
        expect_attr(self.loc, "accept", accept, timeout=timeout)

    def expect_width(self, width: StyleValue, *, timeout: Timeout = None) -> None:
        expect_el_style(self.loc_container, "width", width, timeout=timeout)

    def expect_button_label(
        self,
        button_label: TextValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        if button_label is None:
            button_label = ""
        playwright_expect(self.loc_button).to_have_text(button_label, timeout=timeout)

    def expect_capture(
        self,
        capture: typing.Union[Literal["environment", "user"], None],
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "capture", capture, timeout=timeout)

    def expect_placeholder_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_attr(self.loc_file_display, "placeholder", value=value, timeout=timeout)


class _InputSliderBase(_WidthLocM, _InputWithLabel):
    # id: str,
    # label: TagChildArg,
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
            loc_label=f"label#{id}-label",
        )
        self.loc_irs = self.loc_container.locator("> .irs.irs--shiny")
        self.loc_irs_ticks = self.loc_irs.locator("> .irs-grid > .irs-grid-text")
        self.loc_play_pause = self.loc_container.locator(
            "> .slider-animate-container a"
        )

    def expect_tick_labels_to_have_text(
        self,
        value: typing.List[PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
        playwright_expect(self.loc_irs_ticks).to_have_text(value, timeout=timeout)

    def expect_animate(self, exists: bool, *, timeout: Timeout = None) -> None:
        animate_count = 1 if exists else 0
        playwright_expect(self.loc_play_pause).to_have_count(animate_count)

    # This method doesn't feel like it should accept text as the user does not control the value
    # They only control either `True` or `False`
    def expect_animate_options(
        self,
        *,
        loop: bool = True,
        interval: float = 500,
        # TODO-barret; Use the types below; Make expectations conditional
        # loop: typing.Union[bool, MISSING_TYPE] = MISSING,
        # interval: typing.Union[float, MISSING_TYPE] = MISSING,
        timeout: Timeout = None,
    ) -> None:
        if not loop:
            loop_str = None
        else:
            loop_str = ""
        interval_str = str(interval)

        # TODO-future; Composable expectations
        self.expect_animate(exists=True, timeout=timeout)
        expect_attr(
            self.loc_play_pause,
            "data-loop",
            loop_str,
            timeout=timeout,
        )
        expect_attr(
            self.loc_play_pause,
            "data-interval",
            interval_str,
            timeout=timeout,
        )

    # No `toggle` method as short animations with no loops can cause the button to
    # become `play` over and over again. Instead, have explicit `play` and `pause`
    # methods.
    def click_play(self, *, timeout: Timeout = None) -> None:
        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)
        expect_class_value(
            self.loc_play_pause, "playing", has_class=False, timeout=timeout
        )
        self.loc_play_pause.click()

    def click_pause(self, *, timeout: Timeout = None) -> None:
        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)
        expect_class_value(
            self.loc_play_pause, "playing", has_class=True, timeout=timeout
        )
        self.loc_play_pause.click()

    def expect_min_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_attr(self.loc, "data-min", value=value, timeout=timeout)

    def expect_max_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_attr(self.loc, "data-max", value=value, timeout=timeout)

    def expect_step_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_attr(self.loc, "data-step", value=value, timeout=timeout)

    def expect_ticks_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_attr(self.loc, "data-grid", value=value, timeout=timeout)

    def expect_sep_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_attr(self.loc, "data-prettify-separator", value=value, timeout=timeout)

    def expect_pre_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_attr(self.loc, "data-prefix", value=value, timeout=timeout)

    def expect_post_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_attr(self.loc, "data-postfix", value=value, timeout=timeout)

    # def expect_data_type_to_have_value(
    #     self, value: AttrValue, *, timeout: Timeout = None
    # ) -> None:
    #     expect_attr(self.loc, "data-data-type", value=value, timeout=timeout)

    def expect_time_format_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_attr(self.loc, "data-time-format", value=value, timeout=timeout)

    def expect_timezone_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
        expect_attr(self.loc, "data-timezone", value=value, timeout=timeout)

    def expect_drag_range_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ) -> None:
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
        direction: typing.Union[Literal["left"], Literal["right"]],
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
        grid = self.loc_container.locator(".irs-grid")
        grid_bb = grid.bounding_box(timeout=timeout)
        if grid_bb is None:
            raise RuntimeError("Couldn't find bounding box for .irs-grid")
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
        value: typing.Tuple[TextValue, TextValue],
        *,
        timeout: Timeout = None,
    ) -> None:
        from_val = value[0]
        to_val = value[1]
        if (from_val is None) and (to_val is None):
            raise ValueError("Both `value` tuple entries cannot be `None`")

        # TODO-future; Composable expectations
        if from_val is not None:
            playwright_expect(self.loc_irs_label_from).to_have_text(
                from_val, timeout=timeout
            )
        if to_val is not None:
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
        value: typing.Tuple[
            typing.Union[str, None],
            typing.Union[str, None],
        ],
        *,
        max_err_values: int = 15,
        timeout: Timeout = None,
    ) -> None:
        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)

        value_from = value[0]
        value_to = value[1]
        if (value_from is None) and (value_to is None):
            raise ValueError("Both `value` tuple entries cannot be `None`")

        handle_from = self.loc_irs.locator("> .irs-handle.from")
        handle_to = self.loc_irs.locator("> .irs-handle.to")
        if value_from is not None:
            # Move `from` handle to the far left
            self._set_fraction(handle_from, 0, name="`from` handle", timeout=timeout)
        if value_to is not None:
            # Move `to` handle to the far right
            self._set_fraction(handle_to, 1, name="`to` handle", timeout=timeout)

        handle_center_from = self._handle_center(
            handle_from, name="`from` handle", timeout=timeout
        )
        grid_bb = self._grid_bb(timeout=timeout)

        # Handles are [possibly] now at their respective extreme value
        # Now let's move them towards the other end until we find the corresponding str

        if value_from is not None:
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
        if value_to is not None:
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
    # label: TagChildArg,
    # value: Optional[Union[date, str]] = None,
    # min: Optional[Union[date, str]] = None,
    # max: Optional[Union[date, str]] = None,
    # format: str = "yyyy-mm-dd",
    # startview: str = "month",
    # weekstart: int = 0,
    # language: str = "en",
    # width: Optional[str] = None,
    # autoclose: bool = True,
    # datesdisabled: Optional[List[str]] = None,
    # daysofweekdisabled: Optional[List[int]] = None,

    # Due to the `language` parameter, we can't use `datetime.date` as a value type

    def expect_value(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        if value is None:
            self.expect.to_be_empty(timeout=timeout)
        else:
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
        value: typing.Union[int, AttrValue],
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
        # TODO-barret; None value supported?
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_attr(self.loc, "data-date-autoclose", value=value, timeout=timeout)

    def expect_datesdisabled(
        self,
        value: typing.Union[typing.List[str], None],
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
        value: typing.Union[typing.List[int], None],
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
            loc_label=f"label#{id}-label",
            loc_container=f"div#{id}.shiny-input-container",
        )


class InputDateRange(_WidthContainerM, _InputWithLabel):
    # id: str,
    # label: TagChildArg,
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
            loc_label=f"label#{id}-label",
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
            typing.Union[str, None],
            typing.Union[str, None],
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
        value: typing.Tuple[
            AttrValue,
            AttrValue,
        ],
        *,
        timeout: Timeout = None,
    ) -> None:
        start_val = value[0]
        end_val = value[1]

        if start_val is None and end_val is None:
            raise ValueError("Both `start_val` and `end_val` can not be `None`")

        # We can not use `[value={value}]` within Locators.
        # The physical `value` attribute is never set, so we can not select on it.
        # We must as the start and end values individually, rather than at the same time like the checkboxgroup input.
        # TODO-future; Composable expectations
        if not (start_val is None):
            self.date_start.expect_value(start_val, timeout=timeout)
        if not (end_val is None):
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
        value: typing.Union[int, AttrValue],
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
        value: TextValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        if value is None:
            value = ""
        playwright_expect(self.loc_separator).to_have_text(value, timeout=timeout)

    # width: Optional[str] = None,

    # autoclose: bool = True,
    def expect_autoclose(
        self,
        value: AttrValue,
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
        value: TextValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        if value is None:
            value = ""
        self.expect.to_have_text(value, timeout=timeout)


class _OutputContainerP(_OutputBaseP, Protocol):
    def expect_container_tag(
        self: _OutputBaseP,
        tag_name: typing.Union[Literal["span", "div"], str],
        *,
        timeout: Timeout = None,
    ) -> None:
        ...


class _OutputContainerM:
    def expect_container_tag(
        self: _OutputBaseP,
        tag_name: typing.Union[Literal["span", "div"], str],
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


class OutputTextVerbatim(_OutputTextValue):
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(page, id=id, loc=f"pre#{id}.shiny-text-output")

    def expect_has_placeholder(
        self, placeholder: bool = False, *, timeout: Timeout = None
    ) -> None:
        expect_class_value(
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

    def expect_height_to_have_value(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_el_style(self.loc, "height", value, timeout=timeout)

    def expect_width_to_have_value(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_el_style(self.loc, "width", value, timeout=timeout)

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

    # TODO-barret; Should we try verify that `recalculating` class is not present?
    def expect_to_be_empty(self, *, timeout: Timeout = None) -> None:
        self.expect.to_be_empty(timeout=timeout)

    def expect_not_to_be_empty(self, *, timeout: Timeout = None) -> None:
        self.expect.not_to_be_empty(timeout=timeout)


# When making selectors, use `xpath` so that direct decendents can be checked
class OutputTable(_OutputBase):
    # id: str,
    # **kwargs: TagAttrArg
    def __init__(self, page: Page, id: str) -> None:
        super().__init__(page, id=id, loc=f"#{id}")

    def expect_cell(
        self,
        text: TextValue,
        row: int,
        col: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        if text is None:
            text = ""
        playwright_expect(
            self.loc.locator(
                f"xpath=./table/tbody/tr[{row}]/td[{col}] | ./table/tbody/tr[{row}]/th[{col}]"
            )
        ).to_have_text(text, timeout=timeout)

    def expect_column_labels(
        self,
        labels: typing.Union[typing.List[PatternOrStr], None],
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
        column: int,
        # Can't use `None` as we don't know how many rows exist
        text: typing.List[PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
        playwright_expect(
            self.loc.locator(f"xpath=./table/tbody/tr/td[{column}]")
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
