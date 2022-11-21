"""Barret Facade classes for working with Shiny inputs/outputs in Playwright"""

# pyright: reportUnknownMemberType=false

import re
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

import typing

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

AttrValue = typing.Union[str, typing.Pattern[str]]
StyleValue = typing.Union[str, typing.Pattern[str]]

Timeout = typing.Union[float, None]


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
    attr_name: str,
    value: typing.Union[AttrValue, None],
    timeout: Timeout = None,
):
    """Expect an attribute to have a value. If `value` is `None`, then the attribute should not exist."""
    if isinstance(value, type(None)):
        # if isinstance(value, type(None)):
        # Not allowed to have any value for the attribute
        playwright_expect(loc).not_to_have_attribute(
            attr_name, re.compile(r".*"), timeout=timeout
        )
        return

    playwright_expect(loc).to_have_attribute(attr_name, value, timeout=timeout)


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


class InputWithContainer:
    # timeout: Timeout
    id: str
    container: Locator
    loc: Locator

    def __init__(
        self,
        page: Page,
        *,
        id: str,
        loc: str,
        loc_container: str = "div.shiny-input-container",
    ):
        self.page = page
        # Needed?!? This is covered by `self.loc_root` and possibly `self.loc`
        self.id = id
        self.loc_container = page.locator(loc_container).filter(has=page.locator(loc))
        self.loc = self.loc_container.locator(loc)

    @property
    def expect(self):
        return playwright_expect(self.loc)

    # # Requires a PR to playwright to call `obj.__expect__()` method; Desired API
    # def __expect__(self) -> LocatorAssertions:
    #     return playwright_expect(self.loc)


class InputWithLabel(InputWithContainer):
    def __init__(
        self,
        page: Page,
        *,
        id: str,
        loc: str,
        loc_container: str = "div.shiny-input-container",
    ):
        super().__init__(
            page,
            id=id,
            loc_container=loc_container,
            loc=loc,
        )

        self.loc_label = self.loc_container.locator("label")

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


######################################################
# # Outputs
######################################################


class OutputSimple:
    id: str
    loc: Locator

    def __init__(
        self,
        page: Page,
        *,
        id: str,
        loc: str,
    ):
        self.page = page
        self.id = id
        self.loc = page.locator(loc)

    @property
    def expect(self):
        return playwright_expect(self.loc)


class OutputTextBase(OutputSimple):
    # cls = "shiny-text-output" + (" noplaceholder" if not placeholder else "")
    # return tags.pre(id=resolve_id(id), class_=cls)

    def __init__(self, page: Page, id: str, loc: str):
        super().__init__(
            page,
            id=id,
            loc=loc,
        )

    def value(self, *, timeout: Timeout = None) -> typing.Union[str, None]:
        return self.loc.text_content(timeout=timeout)

    def expect_value(self, value: str, *, timeout: Timeout = None):
        self.expect.to_have_text(value, timeout=timeout)


class OutputText(OutputTextBase):
    def __init__(
        self,
        page: Page,
        id: str,
        *,
        inline: bool = False,
        container_tag: typing.Union[str, None] = None,
    ):
        if container_tag is None:
            container_tag = "span" if inline else "div"
        super().__init__(page, id=id, loc=f"{container_tag}#{id}.shiny-text-output")


class OutputTextVerbatim(OutputTextBase):
    def __init__(self, page: Page, id: str):
        super().__init__(page, id=id, loc=f"pre#{id}.shiny-text-output")

    def expect_has_placeholder(
        self, has_placeholder: bool = False, *, timeout: Timeout = None
    ):
        if has_placeholder:
            self.expect.to_have_class("noplaceholder", timeout=timeout)
        else:
            self.expect.not_to_have_class("noplaceholder", timeout=timeout)
