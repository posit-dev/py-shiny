"""Barret Facade classes for working with Shiny inputs/outputs in Playwright"""
import datetime
import json
import pathlib
import re
import sys

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol
else:
    from typing_extensions import Literal
    from typing_extensions import Protocol

import typing

from playwright.sync_api import FilePayload, Locator, Page
from playwright.sync_api import expect as playwright_expect

"""
Questions:
* While `expect_*_to_have_value()` matches the setup of `expect(x).to_have_value()`, it is a bit verbose. Should we just use `expect_*()` as we only use it in a single context? (Only adding the suffix if other methods like `to_have_html()` or `to_have_text()` would make sense.)
    * Ans: Try things out
* `_DateBase` is signaled as private, but `InputDateRange` will have two fields of `date_start` and `date_end`. Due to how the init selectors are created, they are not `InputDate` instances. Should we make `_DateBase` public?
* Can Date pickers set the `value` attribute on the corresponding input element? If so, we could use `expect_value()` to check the value of the input element.
* In `test_output_table.py`, why can't I write `barret = ["1", "2"]; table.expect_column_labels(barret)`? (Typing issue)

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
"""

OptionalStr = typing.Optional[str]
OptionalInt = typing.Optional[int]

PatternOrStr = typing.Union[str, typing.Pattern[str]]
TextValue = typing.Union[PatternOrStr, None]
AttrValue = typing.Union[PatternOrStr, None]
StyleValue = typing.Union[PatternOrStr, None]

Timeout = typing.Union[float, None]
InitLocator = typing.Union[Locator, str]


def assert_el_has_class(loc: Locator, cls: str):
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
):
    """Expect an attribute to have a value. If `value` is `None`, then the attribute should not exist."""
    if value is None:
        # if isinstance(value, type(None)):
        # Not allowed to have any value for the attribute
        playwright_expect(loc).not_to_have_attribute(
            name, re.compile(r".*"), timeout=timeout
        )
        return

    playwright_expect(loc).to_have_attribute(name=name, value=value, timeout=timeout)


def get_el_style(
    loc: Locator,
    css_key: str,
    timeout: Timeout = None,
):
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
):
    """Expect a style to have a value. If `value` is `None`, then the style should not exist."""
    if isinstance(css_value, type(None)):
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


def expect_multiple(loc: Locator, multiple: bool, timeout: Timeout = None):
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
    ):
        self.page = page
        # Needed?!? This is covered by `self.loc_root` and possibly `self.loc`
        self.id = id
        if isinstance(loc, str):
            loc = page.locator(loc)
        self.loc = loc

    @property
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
    ):

        loc_is_str = isinstance(loc, str)
        loc_container_is_str = isinstance(loc_container, str)

        if loc_is_str and loc_container_is_str:
            loc_container = page.locator(loc_container).filter(
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
    ):
        super().__init__(
            page,
            id=id,
            loc_container=loc_container,
            loc=loc,
        )

        if isinstance(loc_label, str):
            loc_label = self.loc_container.locator(loc_label)
        self.loc_label = loc_label

    def value_label(self, *, timeout: Timeout = None) -> typing.Optional[str]:
        return self.loc_label.text_content(timeout=timeout)

    def expect_label_to_have_text(
        self,
        value: TextValue,
        *,
        timeout: Timeout = None,
    ):
        if value is None:
            value = ""
        playwright_expect(self.loc_label).to_have_text(value, timeout=timeout)


# Class definitions
# * Fields
#   * Try to mirror playwright as much as possible.
#   * There are no properties, only methods; This allows for timeout values to be passed through and for complex methods.
#     * Locators will stay as properties
#   * Don't sub-class. For now, use `_` separatation and use `loc` or `value` as a prefix
# * Approach
#   * Use locators / playwright_expect as much as possible
#     * It should not be necessary to use `assert` directly.
#     * MUST wait for `Locator`s to do their job
#   * Provide `value` methods as a convenience


class _WidthLoc:
    def value_width(
        self: _InputBaseP,
        *,
        timeout: Timeout = None,
    ) -> typing.Optional[str]:
        return str_attr(self.loc, "width", timeout=timeout)

    def expect_width_to_have_value(
        self: _InputBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "width", value=value, timeout=timeout)


class _WidthContainer:
    def value_width(
        self: _InputWithContainerP, *, timeout: Timeout = None
    ) -> typing.Optional[str]:
        return str_attr(self.loc_container, "width", timeout=timeout)

    def expect_width_to_have_value(
        self: _InputWithContainerP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc_container, "width", value=value, timeout=timeout)


class InputNumeric(
    _WidthLoc,
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
    def __init__(self, page: Page, id: str):
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}[type=number].shiny-bound-input",
        )

    def set(self, value: typing.Union[float, str, None], *, timeout: Timeout = None):
        if value is None:
            value = ""
        self.loc.fill(str(value), timeout=timeout)

    def value(self, *, timeout: Timeout = None) -> float:
        # Should we use jquery?
        # return self.loc_label.evaluate("el => $(el).val()", timeout=timeout)

        # # TODO int or float depending on step size?
        # step_val = step_fn(timeout)

        # conv_method = int
        # if step_val is None or not step_val.is_integer():
        #     conv_method = float
        # value = self.loc.input_value()
        # return conv_method(value)

        return float(self.loc.input_value(timeout=timeout))

    def value_min(self, *, timeout: Timeout = None) -> typing.Optional[float]:
        return float_attr(self.loc, "min", timeout=timeout)

    def value_max(self, *, timeout: Timeout = None) -> typing.Optional[float]:
        return float_attr(self.loc, "max", timeout=timeout)

    def value_step(self, *, timeout: Timeout = None) -> typing.Optional[float]:
        return float_attr(self.loc, "step", timeout=timeout)

    def expect_value(
        self,
        value: TextValue,
        *,
        timeout: Timeout = None,
    ):
        if value is None:
            value = ""
        self.expect.to_have_value(value, timeout=timeout)

    def expect_min_to_have_value(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "min", value=value, timeout=timeout)

    def expect_max_to_have_value(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "max", value=value, timeout=timeout)

    def expect_step_to_have_value(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "step", value=value, timeout=timeout)


class _Spellcheck:
    def value_spellcheck(
        self: _InputBaseP,
        *,
        timeout: Timeout = None,
    ) -> typing.Optional[str]:
        return str_attr(self.loc, "spellcheck", timeout=timeout)

    def expect_spellcheck_to_have_value(
        self: _InputBaseP,
        value: typing.Union[Literal["true", "false"], None],
        *,
        timeout: Timeout = None,
    ):
        # self.spellcheck.expect_to_have_value(value, timeout=timeout)
        expect_attr(self.loc, "spellcheck", value=value, timeout=timeout)


class _Placeholder:
    def value_placeholder(
        self: _InputBaseP,
        *,
        timeout: Timeout = None,
    ) -> typing.Optional[str]:
        return str_attr(self.loc, "placeholder", timeout=timeout)

    def expect_placeholder_to_have_value(
        self: _InputBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "placeholder", value=value, timeout=timeout)


class _Autocomplete:
    def value_autocomplete(
        self: _InputBaseP,
        *,
        timeout: Timeout = None,
    ) -> typing.Optional[str]:
        return str_attr(self.loc, "autocomplete", timeout=timeout)

    def expect_autocomplete_to_have_value(
        self: _InputBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "autocomplete", value=value, timeout=timeout)


class InputText(
    _WidthLoc,
    _Placeholder,
    _Autocomplete,
    _Spellcheck,
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
    def __init__(self, page: Page, id: str):
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}[type=text].shiny-bound-input",
        )

        self.loc_label = self.loc_container.locator("label")

    def set(self, value: typing.Union[str, None], *, timeout: Timeout = None):
        if value is None:
            value = ""
        self.loc.fill(str(value), timeout=timeout)

    def value(self, *, timeout: Timeout = None) -> str:
        return self.loc.input_value(timeout=timeout)

    def expect_value(
        self,
        value: TextValue,
        *,
        timeout: Timeout = None,
    ):
        if value is None:
            value = ""
        self.expect.to_have_value(value, timeout=timeout)


class InputPassword(
    _Placeholder,
    _InputWithLabel,
):
    # id: str,
    # label: TagChildArg,
    # value: str = "",
    # *,
    # width: Optional[str] = None,
    # placeholder: Optional[str] = None,
    ...

    def __init__(self, page: Page, id: str):
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}[type=password].shiny-bound-input",
        )

        self.loc_label = self.loc_container.locator("label")

    def set(self, value: typing.Union[str, None], *, timeout: Timeout = None):
        if value is None:
            value = ""
        self.loc.fill(value, timeout=timeout)

    def value(self, *, timeout: Timeout = None) -> str:
        return self.loc.input_value(timeout=timeout)

    def expect_value(
        self,
        value: TextValue,
        *,
        timeout: Timeout = None,
    ):
        if value is None:
            value = ""
        self.expect.to_have_value(value, timeout=timeout)

    def get_width(self, *, timeout: Timeout = None) -> typing.Optional[str]:
        return get_el_style(self.loc_container, "width", timeout=timeout)

    # This class does not inherit from `_WidthContainer`
    # as the width is in the element style
    def expect_width_to_have_value(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_el_style(self.loc_container, "width", value, timeout=timeout)


Resize = Literal["none", "both", "horizontal", "vertical"]


class InputTextArea(_Placeholder, _Autocomplete, _Spellcheck, _InputWithLabel):
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
    def __init__(self, page: Page, id: str):
        super().__init__(
            page,
            id=id,
            loc=f"textarea#{id}.shiny-bound-input",
        )

    def set(self, value: str, *, timeout: Timeout = None):
        self.loc.fill(value, timeout=timeout)

    def value(self, *, timeout: Timeout = None) -> str:
        return self.loc.input_value(timeout=timeout)

    def value_width(self, *, timeout: Timeout = None) -> OptionalStr:
        return get_el_style(self.loc_container, "width", timeout=timeout)

    def value_height(self, *, timeout: Timeout = None) -> OptionalStr:
        return get_el_style(self.loc_container, "height", timeout=timeout)

    def value_cols(self, *, timeout: Timeout = None) -> OptionalInt:
        return int_attr(self.loc, "cols", timeout=timeout)

    def value_rows(self, *, timeout: Timeout = None) -> OptionalInt:
        return int_attr(self.loc, "rows", timeout=timeout)

    def value_resize(self, *, timeout: Timeout = None) -> typing.Optional[Resize]:
        ret = str_attr(self.loc, "resize", timeout=timeout)
        return typing.cast(Resize, ret)

    def expect_value(
        self,
        value: TextValue,
        *,
        timeout: Timeout = None,
    ):
        if value is None:
            value = ""
        self.expect.to_have_value(value, timeout=timeout)

    def expect_width_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        if value is None:
            expect_el_style(self.loc_container, "width", None, timeout=timeout)
            expect_el_style(self.loc, "width", "100%", timeout=timeout)
        else:
            expect_el_style(self.loc_container, "width", value, timeout=timeout)
            expect_el_style(self.loc, "width", None, timeout=timeout)

    def expect_height_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        expect_el_style(self.loc, "height", value, timeout=timeout)

    def expect_cols_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        expect_attr(self.loc, "cols", value=value, timeout=timeout)

    def expect_rows_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        expect_attr(self.loc, "rows", value=value, timeout=timeout)

    def expect_resize_to_have_value(
        self,
        value: typing.Union[Resize, None],
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "resize", value=value, timeout=timeout)


class _InputSelectBase(_WidthLoc, _InputWithLabel):
    loc_selected: Locator
    loc_choices: Locator
    loc_choice_groups: Locator
    loc_select: Locator

    def __init__(
        self,
        page: Page,
        id: str,
        *,
        select_class: str = "",
    ):
        super().__init__(
            page,
            id=id,
            loc=f"select#{id}.shiny-bound-input{select_class}",
            loc_label=f"label[for='{id}']",
        )
        # `loc_container` does not need to contain selected items
        # But we should have `self.loc` be `self.loc_selected`
        self.loc = self.loc_container.locator("option:checked")
        # Same value
        self.loc_selected = self.loc

        self.loc_select = self.loc_container.locator(f"select#{self.id}")
        self.loc_choices = self.loc_select.locator("option")
        self.loc_choice_groups = self.loc_select.locator("optgroup")
        # self.loc_choice_labels = self.loc_container.locator(
        #     "label",
        #     has=self.page.locator("option"),
        # )

    def set(
        self,
        selected: typing.Union[str, typing.List[str]],
        *,
        timeout: Timeout = None,
    ):
        if isinstance(selected, str):
            selected = [selected]
        self.loc_select.select_option(value=selected, timeout=timeout)

    def expect_choices(
        self,
        # TODO; support patterns?
        choices: typing.Union[typing.List[str], None],
        *,
        timeout: Timeout = None,
    ):
        """Expect choices to be in order"""
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if choices is not None and len(choices) == 0:
            choices = None
        if choices is None:
            playwright_expect(self.loc_choices).to_have_count(0, timeout=timeout)
            return

        _RadioButtonCheckboxGroupBase._expect_locator_values_in_list(
            self,
            "option",
            "choices",
            choices,
            timeout=timeout,
        )

    def expect_selected(
        self,
        selected: typing.Union[typing.List[PatternOrStr], PatternOrStr, None],
        *,
        timeout: Timeout = None,
    ):
        """Expect choices to be in order"""
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if isinstance(selected, list) and len(selected) == 0:
            selected = None
        if selected is None:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        ex_selected = playwright_expect(self.loc_select)
        if isinstance(selected, list):
            ex_selected.to_have_values(selected, timeout=timeout)
        else:
            ex_selected.to_have_value(selected, timeout=timeout)

        # _RadioButtonCheckboxGroupBase._expect_locator_values_in_list(
        #     self,
        #     "option",
        #     "selected",
        #     selected,
        #     timeout=timeout,
        #     is_checked=True,
        # )

    def expect_choice_groups(
        self,
        choice_groups: typing.Union[
            # TODO; support patterns?
            typing.List[str],
            None,
        ],
        *,
        timeout: Timeout = None,
    ):
        """Expect choices to be in order"""
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if choice_groups is not None and len(choice_groups) == 0:
            choice_groups = None
        if choice_groups is None:
            playwright_expect(self.loc_choice_groups).to_have_count(0, timeout=timeout)
            return

        _RadioButtonCheckboxGroupBase._expect_locator_values_in_list(
            self,
            "optgroup",
            "choice_groups",
            choice_groups,
            timeout=timeout,
            key="label",
        )

    def expect_choice_labels(
        self,
        choice_labels: typing.Union[typing.List[PatternOrStr], None],
        *,
        timeout: Timeout = None,
    ):
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if choice_labels is not None and len(choice_labels) == 0:
            choice_labels = None
        if choice_labels is None:
            playwright_expect(self.loc_choices).to_have_count(0, timeout=timeout)
            return
        playwright_expect(
            self.loc_container.locator(f"select#{self.id} option")
        ).to_have_text(choice_labels, timeout=timeout)

    # multiple: bool = False,
    def expect_multiple(self, multiple: bool, *, timeout: Timeout = None):
        expect_multiple(self.loc_select, multiple, timeout=timeout)

    def expect_size_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        expect_attr(
            self.loc_select,
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
    def __init__(self, page: Page, id: str):
        super().__init__(
            page,
            id=id,
            select_class="",
        )

    # selectize: bool = False,
    def expect_selectize(self, selectize: bool, *, timeout: Timeout = None):
        # class_=None if selectize else "form-select",
        ex_selectize = playwright_expect(self.loc_select)
        if selectize:
            ex_selectize.not_to_have_class(re.compile("form-select"), timeout=timeout)
        else:
            ex_selectize.to_have_class(re.compile("form-select"), timeout=timeout)


class InputSelectize(_InputSelectBase):
    def __init__(self, page: Page, id: str):
        super().__init__(
            page,
            id=id,
            select_class=".form-select",
        )


class _InputActionBase(_InputBase):
    # TODO-barret; Should these label methods be different?
    def value_label(self, *, timeout: Timeout = None) -> str:
        """Will include icon if present"""
        return self.loc.inner_html(timeout=timeout)

    def expect_label_to_have_text(
        self,
        value: TextValue,
        *,
        timeout: Timeout = None,
    ):
        """Must include icon if present"""

        if value is None:
            value = ""
        self.expect.to_have_text(value, timeout=timeout)

    def click(self, *, timeout: Timeout = None, **kwargs: typing.Any):
        self.loc.click(timeout=timeout, **kwargs)


class InputActionButton(
    _WidthLoc,
    _InputActionBase,
):
    # label: TagChildArg,
    # icon: TagChildArg = None,
    # width: Optional[str] = None,

    def __init__(
        self,
        page: Page,
        id: str,
    ):
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
    ):
        super().__init__(
            page,
            id=id,
            loc=f"a#{id}.action-button.shiny-bound-input",
        )


# * click:
#     * input_checkbox_group
#     * input_radio_buttons


class InputCheckboxBase(
    _WidthContainer,
    _InputWithLabel,
):
    # label: TagChildArg
    # value: bool = False
    # width: Optional[str] = None
    def __init__(self, page: Page, id: str, loc: InitLocator):
        super().__init__(
            page,
            id=id,
            loc=loc,
        )

    def set(self, value: bool, *, timeout: Timeout = None, **kwargs: typing.Any):
        self.loc.set_checked(value, timeout=timeout, **kwargs)

    def toggle(self, *, timeout: Timeout = None, **kwargs: typing.Any):
        self.loc.click(timeout=timeout, **kwargs)

    def value(self, *, timeout: Timeout = None) -> bool:
        return self.loc.is_checked(timeout=timeout)

    def expect_to_be_checked(self, value: bool, *, timeout: Timeout = None):
        if value:
            self.expect.to_be_checked(timeout=timeout)
        else:
            self.expect.not_to_be_checked(timeout=timeout)


class InputCheckbox(InputCheckboxBase):
    def __init__(
        self,
        page: Page,
        id: str,
    ):
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}[type=checkbox].shiny-bound-input",
        )


class InputSwitch(InputCheckboxBase):
    def __init__(
        self,
        page: Page,
        id: str,
    ):
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}[type=checkbox].shiny-bound-input",
        )


class _RadioButtonCheckboxGroupBase(_InputWithLabel):
    loc_choice_labels: Locator

    def expect_choice_labels(
        self,
        labels: typing.Union[PatternOrStr, typing.List[PatternOrStr]],
        *,
        timeout: Timeout = None,
    ):
        playwright_expect(self.loc_choice_labels).to_have_text(
            labels,
            timeout=timeout,
        )

    def expect_inline(self, inline: bool, *, timeout: Timeout = None):
        if inline:
            playwright_expect(self.loc_container).to_have_class(
                "shiny-input-container-inline", timeout=timeout
            )
        else:
            playwright_expect(self.loc_container).not_to_have_class(
                "shiny-input-container-inline", timeout=timeout
            )

    def _expect_locator_values_in_list(
        self: _InputWithContainerP,
        el_type: str,
        arr_name: str,
        # TODO; support patterns?
        arr: typing.List[str],
        *,
        is_checked: typing.Optional[bool] = None,
        timeout: Timeout = None,
        key: str = "value",
    ):
        # Make sure the locator has all of arr

        # Make sure the locator has len(uniq_arr) input elements
        assert len(arr) == len(list(dict.fromkeys(arr))), f"`{arr_name}` must be unique"

        if is_checked is None:
            is_checked_str = ""
        elif is_checked:
            is_checked_str = ":checked"
        else:
            NotImplementedError("`is_checked = FALSE` is not verified yet")
            is_checked_str = ":not(:checked)"

        # Find all items in set
        loc_container = self.loc_container
        for (item, i) in zip(arr, range(len(arr))):
            # # Simple approach if position wasn't needed
            # has_locator = self.page.locator(
            #     f"{el_type}[{key}='{item}']{is_checked_str}"
            # )

            has_locator = self.page.locator(f"{el_type}{is_checked_str}")
            # Go up one element as CSS does not have "self" selector
            # We can leverage this as the HTML structure is very nested.
            # This approach will break if there are matching siblings
            has_locator = has_locator.nth(i).locator("..")
            # Find direct child that matches selector
            has_locator = has_locator.locator(
                f"> {el_type}[{key}='{item}']{is_checked_str}"
            )

            loc_container = loc_container.locator(
                # Return self
                "xpath=.",
                has=has_locator,
            )
        # Make sure other items are not in set
        loc_inputs = loc_container.locator(f"{el_type}{is_checked_str}")
        # TODO-barret; Look into adding a try-catch around this and then performing the locator check using multiple expectations to get better error messages
        playwright_expect(loc_inputs).to_have_count(len(arr), timeout=timeout)


class InputCheckboxGroup(
    _WidthContainer,
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
    ):
        super().__init__(
            page,
            id=id,
            loc="label input[type=checkbox]",
            loc_container=f"div#{id}.shiny-input-checkboxgroup.shiny-bound-input",
            loc_label=f"label#{id}-label",
        )

        # `loc_container` does not need to contain checked items
        # But we should have `self.loc` be `self.loc_selected`
        self.loc = self.loc_container.locator("label input[type=checkbox]:checked")
        # Same value
        self.loc_selected = self.loc

        self.loc_choices = self.loc_container.locator("label input[type=checkbox]")
        self.loc_choice_labels = self.loc_container.locator(
            "label",
            has=self.page.locator("input[type=checkbox]"),
        )

    def set(
        self,
        selected: typing.Union[str, typing.List[str]],
        *,
        timeout: Timeout = None,
        **kwargs: typing.Any,
    ):

        if isinstance(selected, str):
            selected = [selected]
        # We are wanting to delay retriving the value of the checkbox as long as possible
        checkbox_loc = self.loc_choices
        checkbox_loc.nth(0).wait_for(state="attached", timeout=timeout)

        # TODO-barret; Could do with multiple locator calls, but unchecking the values without the known values would be difficult.
        for checkbox in checkbox_loc.element_handles():
            checkbox_value = checkbox.input_value(timeout=timeout)
            checkbox.set_checked(checkbox_value in selected, timeout=timeout, **kwargs)

    def expect_choices(
        self,
        # TODO; support patterns?
        choices: typing.List[str],
        *,
        timeout: Timeout = None,
    ):
        self._expect_locator_values_in_list(
            "input[type=checkbox]",
            "choices",
            choices,
            timeout=timeout,
        )

    def expect_selected(
        self,
        # TODO; support patterns?
        selected: typing.Union[typing.List[str], None],
        *,
        timeout: Timeout = None,
    ):
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if selected is not None and len(selected) == 0:
            selected = None
        if selected is None:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        self._expect_locator_values_in_list(
            "input[type=checkbox]",
            "selected",
            selected,
            timeout=timeout,
            is_checked=True,
        )


class InputRadioButtons(
    _WidthContainer,
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
    ):
        super().__init__(
            page,
            id=id,
            loc="label input[type=radio]",
            loc_container=f"div#{id}.shiny-input-radiogroup.shiny-bound-input",
            loc_label=f"label#{id}-label",
        )
        # `loc_container` does not need to contain checked items
        # But we should have `self.loc` be `self.loc_selected`
        self.loc = self.loc_container.locator("label input[type=radio]:checked")
        # Same value
        self.loc_selected = self.loc

        self.loc_choices = self.loc_container.locator("label input[type=radio]")
        self.loc_choice_labels = self.loc_container.locator(
            "label",
            has=self.page.locator("input[type=radio]"),
        )

    def set(
        self,
        selected: str,
        *,
        timeout: Timeout = None,
        **kwargs: typing.Any,
    ):

        self.loc_container.locator(
            f"label input[type=radio][value='{selected}']"
        ).check(timeout=timeout)

    def expect_choices(
        self,
        # TODO; support patterns?
        choices: typing.List[str],
        *,
        timeout: Timeout = None,
    ):
        self._expect_locator_values_in_list(
            "input[type=radio]",
            "choices",
            choices,
            timeout=timeout,
        )

    def expect_selected(
        self,
        selected: TextValue,
        *,
        timeout: Timeout = None,
    ):
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if selected is None:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        playwright_expect(self.loc_selected).to_have_value(selected, timeout=timeout)


class InputFile(
    # _Placeholder,
    _InputWithLabel,
):
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
    ):
        super().__init__(
            page,
            id=id,
            loc=f"input[type=file]#{id}",
            loc_label=f"label[id={id}-label]",
        )
        self.loc_file_input = self.loc
        self.loc_button = self.loc_container.locator("label span.btn")
        self.loc_file_display = self.loc_container.locator("input[type=text]")

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
    ):
        self.loc.set_input_files(file_path, timeout=timeout)

    def expect_files(
        self,
        files: typing.Union[str, typing.List[str], None],
        *,
        timeout: Timeout = None,
    ):
        # TODO-barret; Find method to get files, or remove method
        # TODO-barret; Test value being sent to shiny?
        NotImplementedError("`expect_files()` is not implemented")

    def expect_multiple(self, multiple: bool, *, timeout: Timeout = None):
        expect_multiple(self.loc, multiple, timeout=timeout)

    def expect_accept(
        self,
        accept: typing.Union[typing.List[str], AttrValue],
        *,
        timeout: Timeout = None,
    ):
        if isinstance(accept, typing.List):
            accept = ",".join(accept)
        expect_attr(self.loc, "accept", accept, timeout=timeout)

    def expect_width(self, width: StyleValue, *, timeout: Timeout = None):
        expect_el_style(self.loc_container, "width", width, timeout=timeout)

    def expect_button_label(
        self,
        button_label: TextValue,
        *,
        timeout: Timeout = None,
    ):
        if button_label is None:
            button_label = ""
        playwright_expect(self.loc_button).to_have_text(button_label, timeout=timeout)

    def expect_capture(
        self,
        capture: typing.Union[Literal["environment", "user"], None],
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "capture", capture, timeout=timeout)

    def expect_placeholder_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ):
        expect_attr(self.loc_file_display, "placeholder", value=value, timeout=timeout)


class InputSlider(_WidthLoc, _InputWithLabel):
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

    def __init__(
        self,
        page: Page,
        id: str,
    ):
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}",
            loc_label=f"label#{id}-label",
        )

    def expect_value(self, value: AttrValue, *, timeout: Timeout = None):
        # TODO-barret; implement
        NotImplementedError("Need to get the value somehow")

    def set(self, fraction: float, *, timeout: Timeout = None) -> None:
        if fraction > 1 or fraction < 0:
            raise ValueError("`fraction` must be between 0 and 1")

        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)

        handle = self.loc_container.locator(".irs-handle")
        handle_bb = handle.bounding_box(timeout=timeout)
        if handle_bb is None:
            raise RuntimeError("Couldn't find bounding box for .irs-handle")

        handle_center = (
            handle_bb.get("x") + (handle_bb.get("width") / 2),
            handle_bb.get("y") + (handle_bb.get("height") / 2),
        )

        grid = self.loc_container.locator(".irs-grid")
        grid_bb = grid.bounding_box(timeout=timeout)
        if grid_bb is None:
            raise RuntimeError("Couldn't find bounding box for .irs-grid")

        mouse = self.loc_container.page.mouse
        mouse.move(handle_center[0], handle_center[1])
        mouse.down()
        mouse.move(
            grid_bb.get("x") + (fraction * grid_bb.get("width")), handle_center[1]
        )
        mouse.up()

    def expect_animate(self, exists: bool, *, timeout: Timeout = None):
        animate_count = 1 if exists else 0
        playwright_expect(
            self.loc_container.locator(".slider-animate-container")
        ).to_have_count(animate_count)

    def expect_animate_loop_to_have_value(
        self, loop: typing.Union[bool, AttrValue], *, timeout: Timeout = None
    ):
        if isinstance(loop, bool):
            if not loop:
                loop = None
            else:
                loop = "true"

        expect_attr(
            self.loc_container.locator(".slider-animate-container a"),
            "data-loop",
            loop,
            timeout=timeout,
        )

    def expect_animate_interval_to_have_value(
        self, interval: typing.Union[int, AttrValue], *, timeout: Timeout = None
    ):
        interval_str = str(interval) if interval else None
        expect_attr(
            self.loc_container.locator(".slider-animate-container a"),
            "data-interval",
            interval_str,
            timeout=timeout,
        )

    # TODO-barret; Test other animate play button and pause button?
    # Testing the HTML seems like too much.
    # Testing the text seems like it is not useful.

    # TODO-barret; All methods below:
    # Could maybe use better formats for the values, but am going to leave as `str` for now

    def expect_min_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        expect_attr(self.loc, "data-min", value=value, timeout=timeout)

    def expect_max_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        expect_attr(self.loc, "data-max", value=value, timeout=timeout)

    # def expect_from_to_have_value(
    #     self, value: AttrValue, *, timeout: Timeout = None
    # ):
    #     expect_attr(self.loc, "data-from", value=value, timeout=timeout)

    def expect_step_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        expect_attr(self.loc, "data-step", value=value, timeout=timeout)

    def expect_ticks_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        expect_attr(self.loc, "data-grid", value=value, timeout=timeout)

    def expect_sep_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        expect_attr(self.loc, "data-prettify-separator", value=value, timeout=timeout)

    def expect_pre_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        expect_attr(self.loc, "data-prefix", value=value, timeout=timeout)

    def expect_post_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        expect_attr(self.loc, "data-postfix", value=value, timeout=timeout)

    # def expect_data_type_to_have_value(
    #     self, value: AttrValue, *, timeout: Timeout = None
    # ):
    #     expect_attr(self.loc, "data-data-type", value=value, timeout=timeout)

    def expect_time_format_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "data-time-format", value=value, timeout=timeout)

    def expect_timezone_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "data-timezone", value=value, timeout=timeout)

    def expect_drag_range_to_have_value(
        self, value: AttrValue, *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "data-drag-interval", value=value, timeout=timeout)


def _date_str(date: typing.Union[datetime.date, AttrValue]) -> OptionalStr:
    if date is None:
        return None
    elif isinstance(date, typing.Pattern):
        return date.pattern
    elif isinstance(date, datetime.date):
        return str(date)
    else:
        return str(datetime.date.fromisoformat(date))


class _DateBase(_WidthContainer, _InputWithLabel):
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
    def set(
        self: _InputWithContainerP,
        value: typing.Union[datetime.date, str, None],
        *,
        timeout: Timeout = None,
    ):
        value_str = _date_str(value)
        if value_str is None:
            self.loc.fill("", timeout=timeout)
            return

        self.loc.fill(value_str, timeout=timeout)
        # TODO-barret; How to trigger the update without opening the date picker?
        self.loc.evaluate('(el) => $(el).bsDatepicker("update");')

    def expect_value(
        self,
        value: typing.Union[datetime.date, AttrValue],
        *,
        timeout: Timeout = None,
    ):
        # Not using `_date_str()` as we want ability to supply non ISO formatted dates
        if isinstance(value, datetime.date):
            value = str(value)

        if value is None:
            self.expect.to_be_empty(timeout=timeout)
        else:
            self.expect.to_have_value(value, timeout=timeout)

    def expect_min_date(
        self,
        value: typing.Union[datetime.date, AttrValue],
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "data-min-date", value=_date_str(value), timeout=timeout)

    def expect_max_date(
        self,
        value: typing.Union[datetime.date, AttrValue],
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "data-max-date", value=_date_str(value), timeout=timeout)

    def expect_format(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "data-date-format", value=value, timeout=timeout)

    def expect_startview(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "data-date-start-view", value=value, timeout=timeout)

    def expect_weekstart(
        self,
        value: typing.Union[int, AttrValue],
        *,
        timeout: Timeout = None,
    ):
        if isinstance(value, int):
            value = str(value)
        expect_attr(self.loc, "data-date-week-start", value=value, timeout=timeout)

    def expect_language(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "data-date-language", value=value, timeout=timeout)

    # autoclose: bool = True,
    def expect_autoclose(
        self,
        # TODO-barret; None value supported?
        value: typing.Union[AttrValue, bool],
        *,
        timeout: Timeout = None,
    ):
        if isinstance(value, bool):
            value = str(value).lower()
        expect_attr(self.loc, "data-date-autoclose", value=str(value), timeout=timeout)

    def expect_datesdisabled(
        self,
        value: typing.Union[typing.List[str], None],
        *,
        timeout: Timeout = None,
    ):
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
    ):
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
    def __init__(self, page: Page, id: str):
        super().__init__(
            page,
            id=id,
            loc="input[type=text].form-control",
            loc_label=f"label#{id}-label",
            loc_container=f"div#{id}.shiny-input-container",
        )


class InputDateRange(_WidthContainer, _InputWithLabel):
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

    def __init__(self, page: Page, id: str):
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
        # TODO-barret; Should this be a list or a tuple?
        value: typing.Union[
            typing.Tuple[
                typing.Union[datetime.date, str, None],
                typing.Union[datetime.date, str, None],
            ],
            None,
        ],
        *,
        timeout: Timeout = None,
    ):
        if value is None:
            value = (None, None)
        self.date_start.set(value=value[0], timeout=timeout)
        self.date_end.set(value=value[1], timeout=timeout)

    def expect_value(
        self,
        # TODO-barret; Should this be a list or a tuple?
        value: typing.Union[
            typing.Tuple[
                typing.Union[datetime.date, PatternOrStr, None],
                typing.Union[datetime.date, PatternOrStr, None],
            ],
            None,
        ],
        *,
        timeout: Timeout = None,
    ):

        start_val = None
        end_val = None
        if not (value is None):
            # Not using `_date_str()` as we want ability to supply non ISO formatted dates
            start_val = value[0]
            if isinstance(start_val, datetime.date):
                start_val = str(start_val)
            end_val = value[1]
            if isinstance(end_val, datetime.date):
                end_val = str(end_val)

        if start_val is None:
            start_val = ""
        if end_val is None:
            end_val = ""

        # We can not use `[value={value}]` within Locators.
        # The physical `value` attribute is never set, so we can not select on it.
        # We must as the start and end values individually, rather than at the same time like the checkboxgroup input.
        self.date_start.expect_value(start_val, timeout=timeout)
        self.date_end.expect_value(end_val, timeout=timeout)

        # loc_dates = self.loc_container
        # loc_dates = loc_dates.locator(
        #     "xpath=.",
        #     has=self.page.locator(f"input:nth-child(1)[type=text][value={start_val}]"),
        # )
        # loc_dates = loc_dates.locator(
        #     "xpath=.",
        #     has=self.page.locator(f"input:nth-child(3)[type=text][value={end_val}]"),
        # )
        # playwright_expect(loc_dates).to_have_count(
        #     int(not (value is None)),
        #     timeout=timeout,
        # )
        # if False:
        #     # TODO-future?; This should be in a try catch around the item above for better diagnostics
        #     self.date_start.expect_value(start_val, timeout=timeout)
        #     self.date_end.expect_value(end_val, timeout=timeout)

    # min: Optional[Union[date, str]] = None,
    def expect_min_date(
        self,
        value: typing.Union[datetime.date, AttrValue],
        *,
        timeout: Timeout = None,
    ):
        # These values should be the same, so checking both independently seems fair
        self.date_start.expect_min_date(value, timeout=timeout)
        self.date_end.expect_min_date(value, timeout=timeout)

    # max: Optional[Union[date, str]] = None,
    def expect_max_date(
        self,
        value: typing.Union[datetime.date, AttrValue],
        *,
        timeout: Timeout = None,
    ):
        # These values should be the same, so checking both independently seems fair
        self.date_start.expect_max_date(value, timeout=timeout)
        self.date_end.expect_max_date(value, timeout=timeout)

    # format: str = "yyyy-mm-dd",
    def expect_format(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        # These values should be the same, so checking both independently seems fair
        self.date_start.expect_format(value, timeout=timeout)
        self.date_end.expect_format(value, timeout=timeout)

    # startview: str = "month",
    def expect_startview(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        # These values should be the same, so checking both independently seems fair
        self.date_start.expect_startview(value, timeout=timeout)
        self.date_end.expect_startview(value, timeout=timeout)

    # weekstart: int = 0,
    def expect_weekstart(
        self,
        value: typing.Union[int, AttrValue],
        *,
        timeout: Timeout = None,
    ):
        # These values should be the same, so checking both independently seems fair
        self.date_start.expect_weekstart(value, timeout=timeout)
        self.date_end.expect_weekstart(value, timeout=timeout)

    # language: str = "en",
    def expect_language(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        # These values should be the same, so checking both independently seems fair
        self.date_start.expect_language(value, timeout=timeout)
        self.date_end.expect_language(value, timeout=timeout)

    # separator: str = " to ",
    def expect_separator(
        self,
        value: TextValue,
        *,
        timeout: Timeout = None,
    ):
        if value is None:
            value = ""
        playwright_expect(self.loc_separator).to_have_text(value, timeout=timeout)

    # width: Optional[str] = None,

    # autoclose: bool = True,
    def expect_autoclose(
        self,
        value: bool,
        *,
        timeout: Timeout = None,
    ):
        # These values should be the same, so checking both independently seems fair
        self.date_start.expect_autoclose(value, timeout=timeout)
        self.date_end.expect_autoclose(value, timeout=timeout)


######################################################
# # Outputs
######################################################


class _OutputBaseP(Protocol):
    id: str
    loc: Locator


class _OutputBase:
    id: str
    loc: Locator

    def __init__(
        self,
        page: Page,
        *,
        id: str,
        loc: InitLocator,
    ):
        self.page = page
        self.id = id

        if isinstance(loc, str):
            loc = page.locator(loc)
        self.loc = loc

    @property
    def expect(self):
        return playwright_expect(self.loc)


class _OutputTextValue(_OutputBase):
    # cls = "shiny-text-output" + (" noplaceholder" if not placeholder else "")
    # return tags.pre(id=resolve_id(id), class_=cls)

    def value(self, *, timeout: Timeout = None) -> str:
        return self.loc.inner_text(timeout=timeout)

    def expect_value(
        self,
        value: TextValue,
        *,
        timeout: Timeout = None,
    ):
        if value is None:
            value = ""
        self.expect.to_have_text(value, timeout=timeout)


class _OutputContainerP(_OutputBaseP, Protocol):
    expect_container_tag: typing.Callable[
        # [
        #     _OutputBaseP,
        #     typing.Union[Literal["span", "div"], str],
        #     Timeout,
        # ],
        ...,  # TODO-barret; Can't get this to work
        None,
    ]


class _OutputContainer:
    def expect_container_tag(
        self: _OutputBaseP,
        tag_name: typing.Union[Literal["span", "div"], str],
        *,
        timeout: Timeout = None,
    ):
        # Could not find an expect method to find the tag name
        # So trying to perform the expectation manually by waiting for attached state,
        # then asserting

        # Make sure the tag exists
        self.loc.wait_for(state="attached", timeout=timeout)
        # Get the tag name
        # TODO-barret; Can this be done with locator and not an element handle?
        found_tag_name = str(
            self.loc.evaluate_handle(
                "el => el.tagName.toLowerCase()", timeout=timeout
            ).json_value()
        )
        assert (
            tag_name == found_tag_name
        ), f"Container tag is `{found_tag_name}`, not `{tag_name}`"


class _OutputInlineContainer(_OutputContainer):
    def expect_inline(
        self: _OutputContainerP, inline: bool = False, *, timeout: Timeout = None
    ):
        tag_name = "span" if inline else "div"
        self.expect_container_tag(tag_name, timeout=timeout)


class OutputText(_OutputInlineContainer, _OutputTextValue):
    def __init__(
        self,
        page: Page,
        id: str,
    ):
        super().__init__(page, id=id, loc=f"#{id}.shiny-text-output")


class OutputTextVerbatim(_OutputTextValue):
    def __init__(self, page: Page, id: str):
        super().__init__(page, id=id, loc=f"pre#{id}.shiny-text-output")

    def expect_has_placeholder(
        self, placeholder: bool = False, *, timeout: Timeout = None
    ):
        if placeholder:
            self.expect.to_have_class("noplaceholder", timeout=timeout)
        else:
            self.expect.not_to_have_class("noplaceholder", timeout=timeout)


class _OutputImageBase(_OutputInlineContainer, _OutputBase):
    # id: str
    # width: str = "100%"
    # height: str = "400px"
    # inline: bool = False

    def __init__(self, page: Page, id: str, loc_classes: str = ""):
        super().__init__(
            page,
            id=id,
            loc=f"#{id}.shiny-image-output{loc_classes}",
        )
        self.loc_img = self.loc.locator("img")

    loc_img: Locator

    def expect_height_to_have_value(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        self.expect_inline(inline=value is None, timeout=timeout)
        expect_el_style(self.loc, "height", value, timeout=timeout)

    def expect_width_to_have_value(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        self.expect_inline(inline=value is None, timeout=timeout)
        expect_el_style(self.loc, "width", value, timeout=timeout)

    def expect_img_src(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc_img, "src", value, timeout=timeout)

    def expect_img_width(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc_img, "width", value, timeout=timeout)

    def expect_img_height(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc_img, "height", value, timeout=timeout)

    def expect_img_alt(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc_img, "alt", value, timeout=timeout)

    def expect_img_style(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc_img, "style", value, timeout=timeout)


class OutputImage(_OutputImageBase):
    def __init__(self, page: Page, id: str):
        super().__init__(page, id=id)
        self.loc_img = self.loc.locator("img")


class OutputPlot(_OutputImageBase):
    # shiny-plot-output
    # id: str
    # width: str = "100%"
    # height: str = "400px"
    # inline: bool = False
    def __init__(self, page: Page, id: str):
        super().__init__(page, id=id, loc_classes=".shiny-plot-output")


class OutputUi(_OutputContainer, _OutputBase):
    # id: str,
    # inline: bool = False,
    # container: Optional[TagFunction] = None,
    def __init__(self, page: Page, id: str):
        super().__init__(page, id=id, loc=f"#{id}")

    # TODO-barret; Should we do `expect_html_to_have_value()`?
    # Thinking they can call `expect(self.loc).to_have_html(value)` directly as Shiny does not own that value, the user does.


class OutputTable(_OutputBase):
    # id: str,
    # **kwargs: TagAttrArg
    def __init__(self, page: Page, id: str):
        super().__init__(page, id=id, loc=f"#{id}")

    def expect_column_labels(
        self,
        labels: typing.Union[typing.List[PatternOrStr], None],
        *,
        timeout: Timeout = None,
    ):
        if isinstance(labels, list) and len(labels) == 0:
            labels = None

        if labels is None:
            playwright_expect(self.loc.locator("thead th")).to_have_count(
                0, timeout=timeout
            )
        else:
            playwright_expect(self.loc.locator("thead th")).to_have_text(
                labels, timeout=timeout
            )

    def expect_column_text(
        self,
        column: int,
        # Can't use `None` as we don't know how many rows exist
        text: typing.List[PatternOrStr],
        *,
        timeout: Timeout = None,
    ):
        playwright_expect(
            self.loc.locator(f"tbody tr td:nth-child({column})")
        ).to_have_text(
            text,
            timeout=timeout,
        )

    def expect_n_col(
        self,
        n: int,
        *,
        timeout: Timeout = None,
    ):
        playwright_expect(self.loc.locator("thead th")).to_have_count(
            n,
            timeout=timeout,
        )

    def expect_n_row(
        self,
        n: int,
        *,
        timeout: Timeout = None,
    ):
        playwright_expect(self.loc.locator("tbody tr")).to_have_count(
            n,
            timeout=timeout,
        )
