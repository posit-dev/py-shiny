"""Barret Facade classes for working with Shiny inputs/outputs in Playwright"""
import re
import sys

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol
else:
    from typing_extensions import Literal
    from typing_extensions import Protocol

import typing

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

"""
Questions:
* While `expect_*_to_have_value()` matches the setup of `expect(x).to_have_value()`, it is a bit verbose. Should we just use `expect_*()` as we only use it in a single context? (Only adding the suffix if other methods like `to_have_html()` or `to_have_text()` would make sense.)
Done:
* input_action_button
* input_action_link
* input_checkbox
* input_checkbox_group
* input_switch
* input_numeric
* input_text
* input_text_area
* output_text
* output_text_verbatim

Waiting:
* click:
    * input_radio_buttons
* date:
    * input_date
    * input_date_range
* options:
    * input_select
    * input_selectize
* unique:
    * input_file
    * input_password
    * input_slider
* outputs:
    * output_plot
    * output_image
    * output_table
    * output_ui
"""


AttrValue = typing.Union[str, typing.Pattern[str]]
StyleValue = typing.Union[str, typing.Pattern[str]]

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
) -> typing.Union[R, None]:
    ret = loc.get_attribute(attr_name, timeout=timeout)
    if not isinstance(ret, type(None)):
        ret = fn(ret)
    return ret


def float_attr(
    loc: Locator, attr_name: str, timeout: Timeout = None
) -> typing.Union[float, None]:
    return maybe_cast_attr(fn=float, loc=loc, attr_name=attr_name, timeout=timeout)


def str_attr(
    loc: Locator, attr_name: str, timeout: Timeout = None
) -> typing.Union[str, None]:
    return maybe_cast_attr(fn=str, loc=loc, attr_name=attr_name, timeout=timeout)


def int_attr(
    loc: Locator, attr_name: str, timeout: Timeout = None
) -> typing.Union[int, None]:
    return maybe_cast_attr(fn=int, loc=loc, attr_name=attr_name, timeout=timeout)


def expect_attr(
    loc: Locator,
    name: str,
    value: typing.Union[AttrValue, None],
    timeout: Timeout = None,
):
    """Expect an attribute to have a value. If `value` is `None`, then the attribute should not exist."""
    if isinstance(value, type(None)):
        # if isinstance(value, type(None)):
        # Not allowed to have any value for the attribute
        playwright_expect(loc).not_to_have_attribute(
            name, re.compile(r".*"), timeout=timeout
        )
        return

    playwright_expect(loc).to_have_attribute(name=name, value=value, timeout=timeout)


def expect_el_style(
    loc: Locator,
    css_key: str,
    # Str representation for value. Will be put in a regex with `css_key`
    css_value: typing.Union[StyleValue, None],
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


######################################################
# # Inputs
######################################################


class _InputBaseP(Protocol):
    id: str
    loc: Locator
    page: Page


class _InputWithContainerP(_InputBaseP, Protocol):
    loc_container: Locator


class _WidthP(Protocol):
    _loc_width: Locator


class _WidthLocP(_WidthP, Protocol):
    loc: Locator
    ...


class _WidthContainerP(_WidthP, Protocol):
    loc_container: Locator
    ...


# class A:
#     def foo(self) -> "A":
#         return self

# class B(A):
#     def foo(self) -> "B":
#         return self


# from abc import ABC


# class InputA(ABC):
#     @abstractmethod
#     def my_abstract_method(self, arg1):
#         pass


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

    # # Requires a PR to playwright to call `obj.__expect__()` method; Desired API
    # def __expect__(self) -> LocatorAssertions:
    #     return playwright_expect(self.loc)
    def foo(self, x: int, y: int, z: int):
        return x + y + z


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

    def value_label(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return self.loc_label.text_content(timeout=timeout)

    def expect_label_to_have_text(self, value: str, *, timeout: Timeout = None):
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


class _Width:
    _loc_width: Locator

    def value_width(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return str_attr(self._loc_width, "width", timeout=timeout)

    def expect_width_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_attr(self._loc_width, "width", value=value, timeout=timeout)


class _WidthLoc(_Width):
    def __init__(
        self: _WidthLocP,
        *args: typing.Any,
        **kwargs: typing.Any,
    ):
        super().__init__(*args, **kwargs)
        self._loc_width = self.loc


class _WidthContainer(_Width):
    def __init__(
        self: _WidthContainerP,
        *args: typing.Any,
        **kwargs: typing.Any,
    ):
        super().__init__(*args, **kwargs)
        self._loc_width = self.loc_container


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

    def set(self, value: float, *, timeout: Timeout = None):
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

    def value_min(self, *, timeout: Timeout = None) -> typing.Union[float, None]:
        return float_attr(self.loc, "min", timeout=timeout)

    def value_max(self, *, timeout: Timeout = None) -> typing.Union[float, None]:
        return float_attr(self.loc, "max", timeout=timeout)

    def value_step(self, *, timeout: Timeout = None) -> typing.Union[float, None]:
        return float_attr(self.loc, "step", timeout=timeout)

    def expect_value(self, value: str, *, timeout: Timeout = None):
        self.expect.to_have_value(value, timeout=timeout)

    def expect_min_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        assert type(value) is not None
        expect_attr(self.loc, "min", value=value, timeout=timeout)

    def expect_max_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        assert type(value) is not None
        expect_attr(self.loc, "max", value=value, timeout=timeout)

    def expect_step_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "step", value=value, timeout=timeout)


class _Spellcheck:
    def value_spellcheck(
        self: _InputBaseP,
        *,
        timeout: Timeout = None,
    ) -> typing.Union[str, None]:
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
    ) -> typing.Union[str, None]:
        return str_attr(self.loc, "placeholder", timeout=timeout)

    def expect_placeholder_to_have_value(
        self: _InputBaseP,
        value: typing.Union[AttrValue, None],
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "placeholder", value=value, timeout=timeout)


class _Autocomplete:
    def value_autocomplete(
        self: _InputBaseP,
        *,
        timeout: Timeout = None,
    ) -> typing.Union[str, None]:
        return str_attr(self.loc, "autocomplete", timeout=timeout)

    def expect_autocomplete_to_have_value(
        self: _InputBaseP,
        value: typing.Union[AttrValue, None],
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

    def set(self, value: str, *, timeout: Timeout = None):
        self.loc.fill(str(value), timeout=timeout)

    def value(self, *, timeout: Timeout = None) -> str:
        return self.loc.input_value(timeout=timeout)

    def expect_value(self, value: str, *, timeout: Timeout = None):
        self.expect.to_have_value(value, timeout=timeout)


Resize = typing.Union[
    Literal["none"], Literal["both"], Literal["horizontal"], Literal["vertical"]
]


class InputTextArea(_Placeholder, _Autocomplete, _Spellcheck, _InputWithLabel):
    # def input_text_area(
    # id: str,
    # label: TagChildArg,
    # value: str = "",
    # *,
    # width: Optional[str] = None,
    # height: Optional[str] = None,
    # cols: Optional[int] = None,
    # rows: Optional[int] = None,
    # placeholder: Optional[str] = None,
    # resize: Optional[
    #     Union[
    #         Literal["none"], Literal["both"], Literal["horizontal"], Literal["vertical"]
    #     ]
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

    def value_width(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        ret = self.loc_container.get_attribute("style", timeout=timeout) or ""
        m = re.search(r"width:\s*([^\s;]+)", ret)
        if m:
            # Return match
            return m.group(1)
        return None

    def value_height(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        ret = self.loc.get_attribute("style", timeout=timeout) or ""
        m = re.search(r"height:\s*([^\s;]+)", ret)
        if m:
            # Return match
            return m.group(1)
        return None

    def value_cols(self, *, timeout: Timeout = None) -> typing.Union[int, None]:
        return int_attr(self.loc, "cols", timeout=timeout)

    def value_rows(self, *, timeout: Timeout = None) -> typing.Union[int, None]:
        return int_attr(self.loc, "rows", timeout=timeout)

    def value_resize(self, *, timeout: Timeout = None) -> typing.Union[Resize, None]:
        ret = str_attr(self.loc, "resize", timeout=timeout)
        return typing.cast(Resize, ret)

    def expect_value(self, value: str, *, timeout: Timeout = None):
        self.expect.to_have_value(value, timeout=timeout)

    def expect_width_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        if value is None:
            expect_el_style(self.loc_container, "width", None, timeout=timeout)
            expect_el_style(self.loc, "width", "100%", timeout=timeout)
        else:
            expect_el_style(self.loc_container, "width", value, timeout=timeout)
            expect_el_style(self.loc, "width", None, timeout=timeout)

    def expect_height_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_el_style(self.loc, "height", value, timeout=timeout)

    def expect_cols_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "cols", value=value, timeout=timeout)

    def expect_rows_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "rows", value=value, timeout=timeout)

    def expect_resize_to_have_value(
        self,
        value: typing.Union[Resize, None],
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "resize", value=value, timeout=timeout)


class _InputActionBase(_InputBase):
    # TODO-barret; Should these label methods be different?
    def value_label(self, *, timeout: Timeout = None) -> str:
        """Will include icon if present"""
        return self.loc.inner_html(timeout=timeout)

    def expect_label_to_have_text(self, value: str, *, timeout: Timeout = None):
        """Must include icon if present"""
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
        labels: typing.Union[
            str,
            typing.Pattern[str],
            typing.List[typing.Union[str, typing.Pattern[str]]],
        ],
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
        self,
        kind: str,
        arr_name: str,
        arr: typing.List[str],
        *,
        is_checked: typing.Union[bool, None] = None,
        timeout: Timeout = None,
    ):
        # Make sure the locator as all of arr
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
        # for item, i in zip(arr, range(len(arr))):
        for item in arr:
            loc_container = loc_container.locator(
                # self
                "xpath=.",
                # Make sure input exists
                has=self.page.locator(
                    f"label input[type={kind}][value={item}]{is_checked_str}"
                ),
                # TODO-barret; Add location info to Locator
                # has=page.locator(f"label input[type={kind}]{is_checked_str}")
                # .nth(i)
                # .locator(
                #     # self
                #     "xpath=.",
                #     # Make sure input has value
                #     has=page.locator(f"input[value={item}]"),
                # ),
            )
        # make sure other items are not in set
        loc_inputs = loc_container.locator(f"label input[type={kind}]{is_checked_str}")
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

        for checkbox in checkbox_loc.element_handles():
            checkbox_value = checkbox.input_value(timeout=timeout)
            checkbox.set_checked(checkbox_value in selected, timeout=timeout, **kwargs)

    def expect_choices(
        self,
        choices: typing.List[str],
        *,
        timeout: Timeout = None,
    ):
        self._expect_locator_values_in_list(
            "checkbox",
            "choices",
            choices,
            timeout=timeout,
        )

    def expect_selected(
        self,
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
            "checkbox",
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

        # We are wanting to delay retriving the value of the radio as long as possible
        self.loc_choices.nth(0).wait_for(state="attached", timeout=timeout)

        self.loc_container.locator(
            f"label input[type=radio][value='{selected}']"
        ).check(timeout=timeout)

        # for radio_button in self.loc_choices.element_handles():
        #     radio_button_value = radio_button.input_value(timeout=timeout)
        #     radio_button.set_checked(
        #         radio_button_value is selected, timeout=timeout, **kwargs
        #     )

    def expect_choices(
        self,
        choices: typing.List[str],
        *,
        timeout: Timeout = None,
    ):
        self._expect_locator_values_in_list(
            "radio",
            "choices",
            choices,
            timeout=timeout,
        )

    def expect_selected(
        self,
        selected: typing.Union[str, None],
        *,
        timeout: Timeout = None,
    ):
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if selected is None:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        playwright_expect(self.loc_selected).to_have_value(selected, timeout=timeout)


######################################################
# # Outputs
######################################################


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

    def value(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return self.loc.inner_text(timeout=timeout)

    def expect_value(self, value: str, *, timeout: Timeout = None):
        self.expect.to_have_text(value, timeout=timeout)


class OutputText(_OutputTextValue):
    def __init__(
        self,
        page: Page,
        id: str,
    ):
        super().__init__(page, id=id, loc=f"#{id}.shiny-text-output")

    def expect_container_tag(
        self,
        container_tag: typing.Union[Literal["span"], Literal["div"], str],
        timeout: Timeout = None,
    ):
        # Could not find an expect method to find the tag name
        # So trying to perform the expectation manually by waiting for attached state,
        # then asserting

        # Make sure the tag exists
        self.loc.wait_for(state="attached", timeout=timeout)
        # Get the tag name
        tag_name = self.loc.evaluate_handle("el => el.tagName", timeout=timeout)
        assert (
            tag_name is container_tag
        ), f"Container tag is {container_tag}, not {tag_name}"

    def expect_inline(self, inline: bool = False, *, timeout: Timeout = None):
        container_tag = "span" if inline else "div"
        self.expect_container_tag(container_tag=container_tag, timeout=timeout)


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
