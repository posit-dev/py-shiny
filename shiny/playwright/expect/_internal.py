from __future__ import annotations

from playwright.sync_api import Locator
from playwright.sync_api import expect as playwright_expect

from ..._docstring import no_example
from .._types import AttrValue, StyleValue, Timeout
from ._expect import (
    expect_not_to_have_attribute,
    expect_not_to_have_class,
    expect_not_to_have_style,
    expect_to_have_class,
    expect_to_have_style,
)

# NOTE:
# Internal methods only!
# These methods are not meant to be used directly by the user. They are internal methods
# used by the other expect methods to simplify the code and reduce redundancy.


@no_example()
def expect_attribute_to_have_value(
    loc: Locator,
    name: str,
    value: AttrValue,
    *,
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
        expect_not_to_have_attribute(loc, name, timeout=timeout)
        return

    playwright_expect(loc).to_have_attribute(name=name, value=value, timeout=timeout)


def expect_style_to_have_value(
    loc: Locator,
    key: str,
    # Str representation for value. Will be put in a regex with `key`
    value: StyleValue,
    *,
    timeout: Timeout = None,
) -> None:
    """
    Expect the `style` attribute to have a value.

    Parameters
    ----------
    loc
        The Playwright locator to check.
    key
        The CSS key to check.
    value
        The CSS value to check. If `None`, then the style attribute should not exist.
    timeout
        The maximum time to wait for the style to appear.
    """
    if value is None:
        expect_not_to_have_style(loc, key, timeout=timeout)
        return

    expect_to_have_style(loc, key, value, timeout=timeout)


def expect_class_to_have_value(
    loc: Locator,
    class_: str,
    *,
    has_class: bool,
    timeout: Timeout = None,
) -> None:
    """Expect a locator to have (or not to have) a class value"""
    if has_class:
        expect_to_have_class(loc, class_, timeout=timeout)
    else:
        expect_not_to_have_class(loc, class_, timeout=timeout)


def _expect_nav_to_have_header_footer(
    parent_loc: Locator,
    header_id: str,
    footer_id: str,
    *,
    timeout: Timeout = None,
) -> None:
    """
    Expect the DOM structure for a header and footer to be preserved.

    Parameters
    ----------
    parent_loc
        The parent locator to check.
    header_id
        The ID of the header element.
    footer_id
        The ID of the footer element.
    timeout
        The maximum time to wait for the header and footer to appear.
    """
    # assert the DOM structure for page_navbar with header and footer is preserved
    class_attr = parent_loc.get_attribute("class")
    if class_attr and "card" in class_attr:
        complicated_parent_loc = parent_loc.locator(
            "xpath=.",
            has=parent_loc.locator("..").locator(
                f".card-body:has(#{header_id}) + .card-body:has(.tab-content) + .card-body #{footer_id}"
            ),
        )
    else:
        complicated_parent_loc = parent_loc.locator(
            "xpath=.",
            has=parent_loc.locator(f"#{header_id} + .tab-content + #{footer_id}"),
        ).locator("..")
    playwright_expect(complicated_parent_loc).to_have_count(1, timeout=timeout)
