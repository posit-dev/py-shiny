from __future__ import annotations

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

from ...types import MISSING, MISSING_TYPE
from .._types import ListPatternOrStr, Timeout
from ..expect._expect import _attr_match_str, _xpath_match_str
from ._base import is_missing


def assert_arr_is_unique(
    arr: ListPatternOrStr,
    msg: str,
) -> None:
    """
    Assert that the array is unique.

    Parameters
    ----------
    arr
        The array to check.
    msg
        The error message.
    """
    assert len(arr) == len(list(dict.fromkeys(arr))), msg


def checked_css_str(
    is_checked: bool | MISSING_TYPE = MISSING,
) -> str:
    """
    Get the CSS string for checked elements.

    Parameters
    ----------
    is_checked
        Whether the elements are checked. Defaults to `MISSING`.
    """
    if is_missing(is_checked):
        return ""
    if is_checked:
        return ":checked"
    else:
        raise NotImplementedError("`is_checked = FALSE` is not verified yet")
        return ":not(:checked)"


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
    """
    Expect the locator to contain the values in the list.

    The matching values must exist and be in order, but other values may also exist
    within the container.

    Parameters
    ----------
    page
        Playwright `Page` of the Shiny app.
    loc_container
        The container locator.
    el_type
        The element type.
    arr_name
        The variable name.
    arr
        The expected values.
    is_checked
        Whether the elements are checked. Defaults to `MISSING`.
    timeout
        The timeout for the expectation. Defaults to `None`.
    key
        The key. Defaults to `"value"`.
    """
    # Make sure the locator contains all of `arr`
    if not isinstance(arr, list):
        raise TypeError(f"`{arr_name}` must be a list")
    for item in arr:
        if not isinstance(item, str):
            raise TypeError(f"`{arr_name}` must be a list of strings")

    # Make sure the locator has len(uniq_arr) input elements
    assert_arr_is_unique(arr, f"`{arr_name}` must be unique")
    is_checked_str = checked_css_str(is_checked)

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
    alt_verify: bool = False,
) -> None:
    """
    Expect the locator to contain the values in the list.

    The matching values must exist and be in order. No other matching values will be
    allowed within the container.

    Parameters
    ----------
    page
        Playwright `Page` of the Shiny app.
    loc_container
        The container locator.
    el_type
        The element type locator.
    arr_name
        The array name.
    arr
        The expected values.
    is_checked
        Whether the elements are checked. Defaults to `MISSING`.
    timeout
        The timeout for the expectation. Defaults to `None`.
    key
        The key. Defaults to `"value"`.
    alt_verify
        Determines if multiple expectations should be performed.
        Defaults to `False`, a single (and very complicated) locator is asserted.
        `True` will perform multiple assertions, which have the possibility of being invalid.
        Use in playwright bug situations only.
    """
    # Make sure the locator has exactly `arr` values

    # Make sure the locator has len(uniq_arr) input elements
    assert_arr_is_unique(arr, f"`{arr_name}` must be unique")

    if isinstance(el_type, Locator):
        if not isinstance(is_checked, MISSING_TYPE):
            raise RuntimeError(
                "`is_checked` cannot be specified if `el_type` is a Locator"
            )
        loc_item = el_type
    else:
        is_checked_str = checked_css_str(is_checked)
        loc_item = page.locator(f"{el_type}{is_checked_str}")

    # If there are no items, then we should not have any elements
    if len(arr) == 0:
        playwright_expect(loc_container.locator(el_type)).to_have_count(
            0, timeout=timeout
        )
        return
    loc_container_orig = loc_container

    def perform_multiple_assertions():
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
        return

    if alt_verify:
        # Accordion has issues where the single locator assertion waits forever within playwright.
        # Perform multiple assertions until playwright fixes bug.
        perform_multiple_assertions()
        return

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
        # Debug expectations
        perform_multiple_assertions()

        # Could not find the reason why. Raising the original error.
        raise e
