"""Barret Facade classes for working with Shiny inputs/outputs in Playwright"""
import re
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

import typing

from playwright.sync_api import ElementHandle, Locator, Page
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


class InputBase:
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


class InputWithContainer(InputBase):
    # timeout: Timeout
    id: str
    container: Locator
    loc: Locator

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


class InputWithLabel(InputWithContainer):
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


class InputNumeric(InputWithLabel):
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

    def value_width(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return str_attr(self.loc, "width", timeout=timeout)

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

    def expect_width_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "width", value=value, timeout=timeout)


class InputText(InputWithLabel):
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

    def value_width(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return str_attr(self.loc, "width", timeout=timeout)

    def value_placeholder(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return str_attr(self.loc, "placeholder", timeout=timeout)

    def value_autocomplete(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return str_attr(self.loc, "autocomplete", timeout=timeout)

    def value_spellcheck(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return str_attr(self.loc, "spellcheck", timeout=timeout)

    def expect_value(self, value: str, *, timeout: Timeout = None):
        self.expect.to_have_value(value, timeout=timeout)

    def expect_width_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "width", value=value, timeout=timeout)

    def expect_placeholder_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "placeholder", value=value, timeout=timeout)

    def expect_autocomplete_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "autocomplete", value=value, timeout=timeout)

    def expect_spellcheck_to_have_value(
        self,
        value: typing.Union[Literal["true", "false"], None],
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "spellcheck", value=value, timeout=timeout)


Resize = typing.Union[
    Literal["none"], Literal["both"], Literal["horizontal"], Literal["vertical"]
]


class InputTextArea(InputWithLabel):
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

    def value_placeholder(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return str_attr(self.loc, "placeholder", timeout=timeout)

    def value_resize(self, *, timeout: Timeout = None) -> typing.Union[Resize, None]:
        ret = str_attr(self.loc, "resize", timeout=timeout)
        return typing.cast(Resize, ret)

    def value_autocomplete(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return str_attr(self.loc, "autocomplete", timeout=timeout)

    def value_spellcheck(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return str_attr(self.loc, "spellcheck", timeout=timeout)

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

    def expect_placeholder_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "placeholder", value=value, timeout=timeout)

    def expect_resize_to_have_value(
        self,
        value: typing.Union[Resize, None],
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "resize", value=value, timeout=timeout)

    def expect_autocomplete_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "autocomplete", value=value, timeout=timeout)

    def expect_spellcheck_to_have_value(
        self,
        value: typing.Union[Literal["true", "false"], None],
        *,
        timeout: Timeout = None,
    ):
        expect_attr(self.loc, "spellcheck", value=value, timeout=timeout)


class InputActionBase(InputBase):
    def __init__(
        self,
        page: Page,
        id: str,
        loc: InitLocator,
    ):
        super().__init__(
            page,
            id=id,
            loc=loc,
        )

    def value_label(self, *, timeout: Timeout = None) -> str:
        """Will return include icon if present"""
        return self.loc.inner_html(timeout=timeout)

    def expect_label_to_have_text(self, value: str, *, timeout: Timeout = None):
        """Must include icon if present"""
        self.expect.to_have_text(value, timeout=timeout)

    def click(self, *, timeout: Timeout = None, **kwargs: typing.Any):
        self.loc.click(timeout=timeout, **kwargs)


class InputActionButton(InputActionBase):
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

    def value_width(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return str_attr(self.loc, "width", timeout=timeout)

    def expect_width_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "width", value=value, timeout=timeout)


class InputActionLink(InputActionBase):
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
            loc=f"a#{id}.action-button.shiny-bound-input",
        )


# * click:
#     * input_checkbox_group
#     * input_radio_buttons


class InputCheckboxBase(InputWithLabel):
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

    def value_width(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return str_attr(self.loc_container, "width", timeout=timeout)

    def expect_width_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_attr(self.loc_container, "width", value=value, timeout=timeout)


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


CheckboxGroupItem = typing.NamedTuple(
    "CheckboxGroupItem",
    is_checked=bool,
    label=str,
    value=str,
)


class InputCheckboxGroup(InputWithLabel):
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
        self.loc = self.loc_container.locator("label input[type=checkbox]:checked")
        # Same value
        self.loc_selected = self.loc
        self.loc_choices = self.loc_container.locator("label input[type=checkbox]")
        self.loc_choice_labels = self.loc_container.locator(
            "label", has=self.page.locator("input[type=checkbox]")
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
        # However, we should not mix different retrieval times of labels and checkboxes.
        # Once labels are attached and retrieved, we can grab checkboxes from within each label
        checkbox_loc = self.loc_choices
        checkbox_loc.nth(0).wait_for(state="attached", timeout=timeout)

        for checkbox in checkbox_loc.element_handles():
            checkbox_value = checkbox.input_value(timeout=timeout)
            checkbox.set_checked(checkbox_value in selected, timeout=timeout, **kwargs)

    # def selected_labels(self, *, timeout: Timeout = None) -> Locator:
    #     return self.loc.locator("label", has=self.page.locator("input:checked"))

    def value_width(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return str_attr(self.loc_container, "width", timeout=timeout)

    def expect_width_to_have_value(
        self, value: typing.Union[AttrValue, None], *, timeout: Timeout = None
    ):
        expect_attr(self.loc_container, "width", value=value, timeout=timeout)

    # def _choices(self, *, timeout: Timeout = None) -> typing.List[CheckboxGroupItem]:
    #     self.loc_choice_labels.wait_for(state="attached", timeout=timeout)
    #     labels = self.loc_choice_labels.element_handles()

    #     ret: typing.List[CheckboxGroupItem] = []
    #     for label_el in labels:
    #         checkbox_el = typing.cast(
    #             ElementHandle, label_el.query_selector("input[type=checkbox]")
    #         )
    #         value = checkbox_el.input_value(timeout=timeout)
    #         is_checked = checkbox_el.is_checked()  # No timeout param
    #         label = label_el.inner_text()
    #         ret.append(
    #             CheckboxGroupItem(
    #                 is_checked=is_checked,
    #                 label=label,
    #                 value=value,
    #             )
    #         )
    #     return ret

    # def value_choices(self, *, timeout: Timeout = None) -> typing.List[str]:
    #     return [choice.value for choice in self._choices(timeout=timeout)]

    #     checkbox_loc = self.loc.locator("input[type=checkbox]")
    #     checkbox_loc.wait_for(state="attached", timeout=timeout)
    #     return [
    #         checkbox.input_value(timeout=timeout)
    #         for checkbox in checkbox_loc.element_handles()
    #     ]

    #     choices = typing.cast(
    #         # typing.List[str], check_labels.inner_text(timeout=timeout)
    #     )
    #     return choices

    #     check_labels = self.loc.locator("label")
    #     choices = typing.cast(
    #         typing.List[str], check_labels.inner_text(timeout=timeout)
    #     )
    #     return choices

    #     # return self.loc.locator("input[type=checkbox]").input_value(timeout=timeout)
    #     # el_handles = self.loc.locator("input[type=checkbox]").element_handles()
    #     # choices: typing.List[str] = []
    #     # for el_handle in el_handles:
    #     #     # el_handle.scroll_into_view_if_needed(timeout=timeout)
    #     #     # el_handle.wait_for_element_state("stable", timeout=timeout)
    #     #     # el_handle.wait_for_element_state("enabled", timeout=timeout)
    #     #     val: str = el_handle.input_value(timeout=timeout)
    #     #     choices.append(val)
    #     # return choices

    # def value_selected(self, *, timeout: Timeout = None) -> typing.List[str]:
    #     # return [
    #     #     choice.value
    #     #     for choice in self._choices(timeout=timeout)
    #     #     if choice.is_checked
    #     # ]
    #     checkbox_loc = self.loc.locator("input[type=checkbox]")
    #     checkbox_loc.wait_for(state="attached", timeout=timeout)
    #     return [
    #         checkbox.input_value(timeout=timeout)
    #         for checkbox in checkbox_loc.element_handles()
    #         if checkbox.is_checked()
    #     ]

    #     # choices = typing.cast(typing.List[str], checkboxes.input_value(timeout=timeout))
    #     # checked_arr = typing.cast(
    #     #     typing.List[bool], checkboxes.is_checked(timeout=timeout)
    #     # )
    #     # return [choice for checked, choice in zip(checked_arr, choices) if checked]

    #     check_labels = self.loc.locator("label")
    #     choices = typing.cast(
    #         typing.List[str], check_labels.inner_text(timeout=timeout)
    #     )
    #     checked_arr = typing.cast(
    #         typing.List[bool], check_labels.locator("input[type=checkbox]").is_checked()
    #     )
    #     selected = [choice for choice, checked in zip(choices, checked_arr) if checked]
    #     return selected

    # def value_choice_labels(self, *, timeout: Timeout = None) -> typing.List[str]:
    #     self.loc_choice_labels
    #     return [choice.label for choice in self._choices(timeout=timeout)]

    #     label_loc = self.loc.locator("label")
    #     label_loc.wait_for(state="attached", timeout=timeout)
    #     return [label.inner_text() for label in label_loc.element_handles()]

    def expect_choices(
        self,
        choices: typing.List[typing.Union[typing.Pattern[str], str]],
        *,
        timeout: Timeout = None,
    ):
        # playwright_expect(self.loc_choices).to_have_value(
        #     value=typing.cast(typing.Union[typing.Pattern[str], str], choices),
        #     timeout=timeout,
        # )
        # Make sure the locator as all choices
        # Make sure the locator has len(uniq_choices) input elements
        # self.loc_choices = self.loc_container.locator("label input")
        uniq_choices = list(dict.fromkeys(choices))
        assert len(uniq_choices) == len(choices), "`choices` must be unique"

        loc_all_choices = self.loc_container
        for choice in uniq_choices:
            loc_all_choices = loc_all_choices.locator(
                # self
                "xpath=.",
                # Make sure input exists
                has=self.page.locator(f"label input[type=checkbox][value={choice}]"),
            )
        loc_all_choices = loc_all_choices.locator("label input[type=checkbox]")
        playwright_expect(loc_all_choices).to_have_count(len(choices), timeout=timeout)

        # input_checkbox_group_choices = self.value_choices(timeout=timeout)
        # assert choices == input_checkbox_group_choices

    def expect_selected(
        self,
        selected: typing.Union[
            typing.List[typing.Union[typing.Pattern[str], str]], None
        ],
        *,
        timeout: Timeout = None,
    ):
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if selected is not None and len(selected) == 0:
            selected = None
        if selected is None:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        # Find all selected checkboxes given their value
        # Find all selected checkboxes and expect count to be N
        uniq_selected = list(dict.fromkeys(selected))
        assert len(uniq_selected) == len(selected), "`selected` must be unique"
        loc_selected = self.loc_container
        for selected_i in uniq_selected:
            loc_selected = loc_selected.locator(
                # self
                "xpath=.",
                # Make sure input exists
                has=self.page.locator(
                    f"label input[type=checkbox][value={selected_i}]:checked"
                ),
            )
        loc_selected = loc_selected.locator("label input[type=checkbox]:checked")
        playwright_expect(loc_selected).to_have_count(len(selected))
        # playwright_expect(self.loc_selected).to_have_value(
        #     value=typing.cast(typing.Union[typing.Pattern[str], str], selected),
        #     timeout=timeout,
        # )
        # input_checkbox_group_selected = self.value_selected(timeout=timeout)
        # assert selected == input_checkbox_group_selected

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
        # input_checkbox_group_labels = self.value_labels(timeout=timeout)
        # assert labels == input_checkbox_group_labels

    def value_inline(self, *, timeout: Timeout = None) -> bool:
        class_val = self.loc_choice_labels.element_handle(
            timeout=timeout
        ).get_attribute("class")
        return re.search(r"checkbox-inline", class_val or "") is not None

    def expect_inline(self, inline: bool, *, timeout: Timeout = None):
        # Check the first input element for the class value
        if inline:
            playwright_expect(self.loc_choice_labels.nth(0)).to_have_class(
                "checkbox-inline", timeout=timeout
            )
        else:
            playwright_expect(self.loc_choice_labels.nth(0)).not_to_have_class(
                "checkbox-inline", timeout=timeout
            )


######################################################
# # Outputs
######################################################


class OutputBase:
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


class OutputTextBase(OutputBase):
    # cls = "shiny-text-output" + (" noplaceholder" if not placeholder else "")
    # return tags.pre(id=resolve_id(id), class_=cls)

    def __init__(self, page: Page, id: str, loc: InitLocator):
        super().__init__(
            page,
            id=id,
            loc=loc,
        )

    def value(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return self.loc.inner_text(timeout=timeout)

    def expect_value(self, value: str, *, timeout: Timeout = None):
        self.expect.to_have_text(value, timeout=timeout)


class OutputText(OutputTextBase):
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


class OutputTextVerbatim(OutputTextBase):
    def __init__(self, page: Page, id: str):
        super().__init__(page, id=id, loc=f"pre#{id}.shiny-text-output")

    def expect_has_placeholder(
        self, placeholder: bool = False, *, timeout: Timeout = None
    ):
        if placeholder:
            self.expect.to_have_class("noplaceholder", timeout=timeout)
        else:
            self.expect.not_to_have_class("noplaceholder", timeout=timeout)
