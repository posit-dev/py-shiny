"""Facade classes for working with Shiny inputs/outputs in Playwright"""

from __future__ import annotations

import re
import sys

from playwright.sync_api import Locator
from playwright.sync_api import expect as playwright_expect

from ..._docstring import no_example
from ..._typing_extensions import assert_type
from .._types import AttrValue, PatternOrStr, PatternStr, StyleValue, Timeout

# Internal method only!
# "_expect_class_value",
__all__ = (
    "expect_attribute_to_have_value",
    "expect_to_have_class",
    "expect_not_to_have_class",
    "expect_to_have_style",
)


@no_example()
def expect_attribute_to_have_value(
    loc: Locator,
    name: str,
    value: AttrValue,
    timeout: Timeout = None,
) -> None:
    """
    Expect an attribute to have a value.

    This method wraps Playwright's Locator expectation `to_have_attribute()` when `value is not `None` and `not_to_have_attribute()` when `value` is `None`. When `value` is `None`, the attribute should not exist and no value should be present.

    Parameters
    ----------
    loc
        The Playwright locator to check.
    name
        The attribute name.
    value
        The attribute value to check. When `value` is `None`, the attribute should not
        exist and no value should be present.
    timeout
        The maximum time to wait for the attribute to appear
    """
    if value is None:
        # Not allowed to have any value for the attribute
        playwright_expect(loc).not_to_have_attribute(
            name, re.compile(r".*"), timeout=timeout
        )
        return

    playwright_expect(loc).to_have_attribute(name=name, value=value, timeout=timeout)


@no_example()
def expect_to_have_class(
    loc: Locator,
    class_: str,
    *,
    timeout: Timeout = None,
) -> None:
    """
    Expect a locator to contain a class value

    This method wraps Playwright's Locator expectation `to_have_class()`. However, Playwright does not have a method to check for individual class values within the elements `class` value. This method will insert the class value into a regex pattern to check for the class value within the `class` attribute according to word boundaries or the start/end of the `class` string.

    Parameters
    ----------
    loc
        The Playwright locator to check.
    class_
        The class value to find.
    timeout
        The maximum time to wait for the class to appear.
    """
    cls_regex = re.compile(rf"(^|\s+){re.escape(class_)}(\s+|$)")
    playwright_expect(loc).to_have_class(cls_regex, timeout=timeout)


@no_example()
def expect_not_to_have_class(
    loc: Locator,
    class_: str,
    *,
    timeout: Timeout = None,
) -> None:
    """
    Expect a locator not to contain a class value

    This method wraps Playwright's Locator expectation `not_to_have_class()`. However
    Playwright does not have a method to check for individual class values within the
    elements `class` value. This method will insert the class value into a regex pattern
    to check for the class value within the `class` attribute according to word
    boundaries or the start/end of the `class` string.

    Parameters
    ----------
    loc
        The Playwright locator to check.
    class_
        The class value that should not be found within the resolved locator.
    timeout
        The maximum time to wait for the class to disappear.
    """
    cls_regex = re.compile(rf"(^|\s+){re.escape(class_)}(\s+|$)")
    playwright_expect(loc).not_to_have_class(cls_regex, timeout=timeout)


@no_example()
def expect_to_have_style(
    loc: Locator,
    css_key: str,
    # Str representation for value. Will be put in a regex with `css_key`
    css_value: StyleValue,
    *,
    timeout: Timeout = None,
) -> None:
    """
    Expect the `style` attribute to have a value.

    Parameters
    ----------
    loc
        The Playwright locator to check.
    css_key
        The CSS key to check.
    css_value
        The CSS value to check. If `None`, then the style attribute should not exist.
    timeout
        The maximum time to wait for the style to appear.
    """
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


def _expect_class_value(
    loc: Locator,
    class_: str,
    has_class: bool,
    timeout: Timeout = None,
) -> None:
    """Expect a locator to have (or not to have) a class value"""
    if has_class:
        expect_to_have_class(loc, class_, timeout=timeout)
    else:
        expect_not_to_have_class(loc, class_, timeout=timeout)


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


def _style_match_str(key: str, value: PatternOrStr) -> PatternStr:
    if isinstance(value, str):
        value_str = re.escape(value)
    else:
        value_str = value.pattern
    return re.compile(rf"(^|;)\s*{re.escape(key)}\s*:\s*{value_str}\s*(;|$)")
