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
    """Expect an attribute to have a value. If `value` is `None`, then the attribute should not exist."""
    if value is None:
        # if isinstance(value, type(None)):
        # Not allowed to have any value for the attribute
        playwright_expect(loc).not_to_have_attribute(
            name, re.compile(r".*"), timeout=timeout
        )
        return

    playwright_expect(loc).to_have_attribute(name=name, value=value, timeout=timeout)


@no_example()
def expect_to_have_class(
    loc: Locator,
    cls: str,
    *,
    timeout: Timeout = None,
) -> None:
    """Expect a locator to contain a class value"""
    cls_regex = re.compile(rf"(^|\s+){re.escape(cls)}(\s+|$)")
    playwright_expect(loc).to_have_class(cls_regex, timeout=timeout)


@no_example()
def expect_not_to_have_class(
    loc: Locator,
    cls: str,
    *,
    timeout: Timeout = None,
) -> None:
    """Expect a locator not to contain a class value"""
    cls_regex = re.compile(rf"(^|\s+){re.escape(cls)}(\s+|$)")
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
