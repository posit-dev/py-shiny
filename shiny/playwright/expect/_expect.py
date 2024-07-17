"""Facade classes for working with Shiny inputs/outputs in Playwright"""

from __future__ import annotations

import re
import sys

from playwright.sync_api import Locator
from playwright.sync_api import expect as playwright_expect

from ..._docstring import no_example
from ..._typing_extensions import assert_type
from .._types import PatternOrStr, PatternStr, Timeout

__all__ = (
    "expect_not_to_have_attribute",
    "expect_to_have_class",
    "expect_not_to_have_class",
    "expect_to_have_style",
    "expect_not_to_have_style",
)


@no_example()
def expect_not_to_have_attribute(
    loc: Locator,
    name: str,
    *,
    timeout: Timeout = None,
) -> None:
    """
    Expect that the attribute does not exist.

    This method wraps Playwright's Locator expectation `not_to_have_attribute()` and
    sets the value to a regular expression that matches anything.

    If you'd like to check for a specific value, use Playwright's
    `expect(loc).to_have_attribute()` method, instead.

    Parameters
    ----------
    loc
        The Playwright locator to check.
    name
        The attribute name that should **not** be found within the resolved locator.
    timeout
        The maximum time to wait for the attribute to appear
    """
    # Not allowed to have any value for the attribute
    playwright_expect(loc).not_to_have_attribute(
        name, re.compile(r".*"), timeout=timeout
    )
    return


@no_example()
def expect_to_have_class(
    loc: Locator,
    class_: str,
    *,
    timeout: Timeout = None,
) -> None:
    """
    Expect a CSS class value is found.

    This method wraps Playwright's Locator expectation [`to_have_class()`
    method](https://playwright.dev/python/docs/api/class-locatorassertions#locator-assertions-to-have-class).
    However, Playwright does not have an easy method to check for individual class
    values _within_ the elements `class` value.

    This method will insert the class value
    into a regex pattern to check for the class value within the `class` attribute
    according to word boundaries or the start/end of the `class` string.

    Parameters
    ----------
    loc
        The Playwright locator to check.
    class_
        The class value to find.
    timeout
        The maximum time to wait for the class to appear.

    See Also
    --------
    * :func:`shiny.playwright.expect.expect_not_to_have_class`
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
    Expect a CSS class value is not found.

    This method wraps Playwright's Locator expectation [`not_to_have_class()`
    method](https://playwright.dev/python/docs/api/class-locatorassertions#locator-assertions-not-to-have-class).
    However, Playwright does not have an easy method to check for individual class
    values _within_ the elements `class` value.

    This method will insert the class string
    value into a regex pattern to check for the class value within the `class` attribute
    according to word boundaries or the start/end of the `class` string.

    Parameters
    ----------
    loc
        The Playwright locator to check.
    class_
        The class value that should **not** be found within the resolved locator.
    timeout
        The maximum time to wait for the class to disappear.

    See Also
    --------
    * :func:`shiny.playwright.expect.expect_to_have_class`
    """
    cls_regex = re.compile(rf"(^|\s+){re.escape(class_)}(\s+|$)")
    playwright_expect(loc).not_to_have_class(cls_regex, timeout=timeout)


@no_example()
def expect_to_have_style(
    loc: Locator,
    key: str,
    # Str representation for value. Will be put in a regex with `css_key`
    value: PatternOrStr,
    *,
    timeout: Timeout = None,
) -> None:
    """
    Expect the `style` attribute to have a value.

    This is different than Playwright's [`to_have_css(key, value)`
    method](https://playwright.dev/python/docs/api/class-locatorassertions#locator-assertions-to-have-css),
    as that method will check for the computed style of the element. Whereas this method
    will check the `style` attribute directly.

    Parameters
    ----------
    loc
        The Playwright locator to check.
    key
        The CSS key to check.
    value
        The CSS value to check.
    timeout
        The maximum time to wait for the style to appear.

    See Also
    --------
    * :func:`shiny.playwright.expect.expect_not_to_have_style`
    """

    playwright_expect(loc).to_have_attribute(
        "style",
        _style_match_str(key, value),
        timeout=timeout,
    )


@no_example()
def expect_not_to_have_style(
    loc: Locator,
    key: str,
    *,
    timeout: Timeout = None,
) -> None:
    """
    Expect a key within `style` attribute to not exist.

    Convenience method to check if a CSS key does not exist within the `style`
    attribute. The `key` is escaped within a regular expression that checks within
    word boundaries or the start/end of the `style` string.

    This is different than Playwright's [`to_have_css(key, value)`
    method](https://playwright.dev/python/docs/api/class-locatorassertions#locator-assertions-to-have-css),
    as that method will check for the computed style of the element. Whereas this method
    will check the `style` attribute directly.

    Parameters
    ----------
    loc
        The Playwright locator to check.
    key
        The CSS key to check.
    timeout
        The maximum time to wait for the style to appear.

    See Also
    --------
    * :func:`shiny.playwright.expect.expect_to_have_style
    """
    # Not allowed to have any value for the style
    playwright_expect(loc).not_to_have_attribute(
        "style",
        re.compile(rf"\b{re.escape(key)}\s*:"),
        timeout=timeout,
    )
    return


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
