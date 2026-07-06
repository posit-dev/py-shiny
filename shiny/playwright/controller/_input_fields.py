from __future__ import annotations

import json
import typing
from typing import Literal

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

from ...types import MISSING_TYPE
from .._types import AttrValue, PatternOrStr, StyleValue, Timeout
from ..expect._internal import (
    expect_attribute_to_have_value as _expect_attribute_to_have_value,
)
from ..expect._internal import expect_class_to_have_value as _expect_class_to_have_value
from ..expect._internal import expect_style_to_have_value as _expect_style_to_have_value
from ._base import (
    Resize,
    UiBaseP,
    UiWithLabel,
    WidthContainerStyleM,
    all_missing,
    not_is_missing,
    set_text,
)


class _SetTextM:
    def set(self: UiBaseP, value: str, *, timeout: Timeout = None) -> None:
        """
        Sets the text value

        Parameters
        ----------
        value
            The text to set.
        timeout
            The maximum time to wait for the text to be set. Defaults to `None`.
        """
        set_text(self.loc, value, timeout=timeout)


class _ExpectTextInputValueM:
    """A mixin class for text input values."""

    def expect_value(
        self: UiBaseP,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the value of the text input to have a specific value.

        Parameters
        ----------
        value
            The expected value of the text input.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        playwright_expect(self.loc).to_have_value(value, timeout=timeout)


class InputNumeric(
    _SetTextM,
    _ExpectTextInputValueM,
    WidthContainerStyleM,
    UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_numeric`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes the input numeric Playwright control.

        Parameters
        ----------
        page
            The page where the input numeric is located.
        id
            The id of the input numeric.
        """
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}[type=number].shiny-bound-input",
        )

    def expect_min(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the minimum numeric value to be a specific value.

        Parameters
        ----------
        value
            The expected minimum numeric value.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "min", value=value, timeout=timeout)

    def expect_max(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the maximum numeric value to be a specific value.

        Parameters
        ----------
        value
            The expected maximum numeric value.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "max", value=value, timeout=timeout)

    def expect_step(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect step value when incrementing/decrementing the numeric input.

        Parameters
        ----------
        value
            The expected step value for the numeric input.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "step", value=value, timeout=timeout)


class _ExpectSpellcheckAttrM:
    """
    A mixin class for the spellcheck attribute.
    """

    def expect_spellcheck(
        self: UiBaseP,
        value: Literal["true", "false"] | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `spellcheck` attribute of the input to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `spellcheck` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        # self.spellcheck.expect_to_have_value(value, timeout=timeout)
        _expect_attribute_to_have_value(
            self.loc, "spellcheck", value=value, timeout=timeout
        )


class _ExpectPlaceholderAttrM:
    def expect_placeholder(
        self: UiBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `placeholder` attribute of the input to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `placeholder` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "placeholder", value=value, timeout=timeout
        )


class _ExpectAutocompleteAttrM:
    def expect_autocomplete(
        self: UiBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `autocomplete` attribute of the input to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `autocomplete` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "autocomplete", value=value, timeout=timeout
        )


class _ExpectRowsAttrM:
    """A mixin class for the rows attribute."""

    def expect_rows(
        self: UiBaseP,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `rows` attribute to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `rows` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "rows", value=value, timeout=timeout)


class InputText(
    _SetTextM,
    _ExpectTextInputValueM,
    WidthContainerStyleM,
    _ExpectPlaceholderAttrM,
    _ExpectAutocompleteAttrM,
    _ExpectSpellcheckAttrM,
    UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_text`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes the input text.

        Parameters
        ----------
        page
            The page where the input text is located.
        id
            The id of the input text.
        """
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}[type=text].shiny-bound-input",
        )


class InputPassword(
    _SetTextM,
    _ExpectTextInputValueM,
    WidthContainerStyleM,
    _ExpectPlaceholderAttrM,
    UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_password`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes the input password.

        Parameters
        ----------
        page
            The page where the input password is located.
        id
            The id of the input password.
        """
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}[type=password].shiny-bound-input",
        )

    # This class does not inherit from `_WidthContainerM`
    # as the width is in the element style
    def expect_width(
        self,
        value: StyleValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `width` attribute of the input password to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `width` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc_container, "width", value, timeout=timeout)


class InputTextArea(
    _SetTextM,
    WidthContainerStyleM,
    _ExpectTextInputValueM,
    _ExpectPlaceholderAttrM,
    _ExpectAutocompleteAttrM,
    _ExpectSpellcheckAttrM,
    _ExpectRowsAttrM,
    UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_text_area`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes the input text area.

        Parameters
        ----------
        page
            The page where the input text area is located.
        id
            The id of the input text area.
        """
        super().__init__(
            page,
            id=id,
            loc=f"textarea#{id}.shiny-bound-input",
        )

    def expect_width(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expect the `width` attribute of the input text area to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `width` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        if value is None:
            _expect_style_to_have_value(
                self.loc_container,
                "width",
                None,
                timeout=timeout,
            )
            _expect_style_to_have_value(self.loc, "width", "100%", timeout=timeout)
        else:
            _expect_style_to_have_value(
                self.loc_container, "width", value, timeout=timeout
            )
            _expect_style_to_have_value(self.loc, "width", None, timeout=timeout)

    def expect_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expect the `height` attribute of the input text area to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `height` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc, "height", value, timeout=timeout)

    def expect_cols(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the `cols` attribute of the input text area to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `cols` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "cols", value=value, timeout=timeout)

    def expect_resize(
        self,
        value: Resize | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `resize` attribute of the input text area to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `resize` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc, "resize", value=value, timeout=timeout)

    def expect_autoresize(
        self,
        value: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `autoresize` attribute of the input text area to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `autoresize` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc,
            "textarea-autoresize",
            has_class=value,
            timeout=timeout,
        )


class _DateBase(
    WidthContainerStyleM,
    _SetTextM,
    UiWithLabel,
):

    # Due to the `language` parameter, we can't use `datetime.date` as a value type

    def expect_value(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        # if value is None:
        #     self.expect.to_be_empty(timeout=timeout)
        # else:
        self.expect.to_have_value(value, timeout=timeout)

    def expect_min_date(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-min-date` attribute value.

        Parameters
        ----------
        value
            The expected `data-min-date` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-min-date", value=value, timeout=timeout
        )

    def expect_max_date(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-max-date` attribute value.

        Parameters
        ----------
        value
            The expected `data-max-date` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-max-date", value=value, timeout=timeout
        )

    def expect_format(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-format` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-format` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-date-format", value=value, timeout=timeout
        )

    def expect_startview(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-start-view` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-start-view` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-date-start-view", value=value, timeout=timeout
        )

    def expect_weekstart(
        self,
        value: int | AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-week-start` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-week-start` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        if isinstance(value, int):
            value = str(value)
        _expect_attribute_to_have_value(
            self.loc, "data-date-week-start", value=value, timeout=timeout
        )

    def expect_language(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-language` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-language` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-date-language", value=value, timeout=timeout
        )

    # autoclose: bool = True,
    def expect_autoclose(
        self,
        value: Literal["true", "false"],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-autoclose` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-autoclose` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-date-autoclose", value=value, timeout=timeout
        )

    def expect_datesdisabled(
        self,
        value: list[str] | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-dates-disabled` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-dates-disabled` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        if isinstance(value, list):
            assert len(value) > 0, "`value` must be `None` or a non-empty list"
        value_str = "null" if value is None else json.dumps(value)
        _expect_attribute_to_have_value(
            self.loc,
            "data-date-dates-disabled",
            value=value_str,
            timeout=timeout,
        )

    def expect_daysofweekdisabled(
        self,
        value: list[int] | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected `data-date-days-of-week-disabled` attribute value.

        Parameters
        ----------
        value
            The expected `data-date-days-of-week-disabled` attribute value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        if isinstance(value, list):
            assert len(value) > 0, "`value` must be `None` or a non-empty list"
        value_str = "null" if value is None else json.dumps(value)
        _expect_attribute_to_have_value(
            self.loc,
            "data-date-days-of-week-disabled",
            value=value_str,
            timeout=timeout,
        )

    def set(self, value: str, *, timeout: Timeout = None) -> None:
        """
        Sets the text value

        Parameters
        ----------
        value
            The text to set.
        timeout
            The maximum time to wait for the text to be set. Defaults to `None`.
        """
        set_text(self.loc, value, timeout=timeout)
        self.loc.press("Enter", timeout=timeout)


class InputDate(_DateBase):
    def __init__(self, page: Page, id: str) -> None:
        """
        Initialize an InputDate object.

        Parameters
        ----------
        page
            The page object.
        id
            The id of the input element.
        """
        super().__init__(
            page,
            id=id,
            loc="input[type=text].form-control",
            loc_container=f"div#{id}.shiny-input-container",
        )


class InputDateRange(WidthContainerStyleM, UiWithLabel):
    """Controller for :func:`shiny.ui.input_date_range`."""

    loc_separator: Locator
    """
    Playwright `Locator` of the separator between the two input elements.
    """
    loc_start: Locator
    """
    Playwright `Locator` of the start date input element.
    """
    loc_end: Locator
    """
    Playwright `Locator` of the end date input element.
    """
    date_start: _DateBase
    """
    The start date input element.
    """
    date_end: _DateBase
    """
    The end date input element.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initialize an InputDateRange object.

        Parameters
        ----------
        page
            The page object.
        id
            The id of the input element.
        """
        super().__init__(
            page,
            id=id,
            loc="input[type=text].form-control",
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
            str | None,
            str | None,
        ],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Sets the value of the input element.

        Parameters
        ----------
        value
            The value to set. The first element is the start date and the second element is the end date.
        timeout
            The maximum time to wait for the value to be set. Defaults to `None`.
        """
        start = value[0]
        end = value[1]
        # TODO-future; Composable set() methods?
        if start is not None:
            self.date_start.set(value=start, timeout=timeout)
        if end is not None:
            self.date_end.set(value=end, timeout=timeout)

    def expect_value(
        self,
        value: (
            typing.Tuple[PatternOrStr, PatternOrStr]
            | typing.Tuple[PatternOrStr, MISSING_TYPE]
            | typing.Tuple[MISSING_TYPE, PatternOrStr]
        ),
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected value.

        Parameters
        ----------
        value
            The expected value. The first element is the start date and the second element is the end date.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        if all_missing(*value):
            raise ValueError("Both `start_val` and `end_val` can not be `MISSING_TYPE`")
        start_val = value[0]
        end_val = value[1]
        # We can not use `[value={value}]` within Locators.
        # The physical `value` attribute is never set, so we can not select on it.
        # We must as the start and end values individually, rather than at the same time like the checkboxgroup input.
        # TODO-future; Composable expectations
        if not_is_missing(start_val):
            self.date_start.expect_value(start_val, timeout=timeout)
        if not_is_missing(end_val):
            self.date_end.expect_value(end_val, timeout=timeout)

    # min: Optional[Union[date, str]] = None,
    def expect_min_date(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected minimum date.

        Parameters
        ----------
        value
            The expected minimum date.
        timeout
            The maximum time to wait for the minimum date to appear. Defaults to `None`.
        """
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
        """
        Asserts that the input element has the expected maximum date.

        Parameters
        ----------
        value
            The expected maximum date.
        timeout
            The maximum time to wait for the maximum date to appear. Defaults to `None`.
        """
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
        """
        Asserts that the input element has the expected format.

        Parameters
        ----------
        value
            The expected format.
        timeout
            The maximum time to wait for the format to appear. Defaults to `None`.
        """
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
        """
        Asserts that the input element has the expected start view.

        Parameters
        ----------
        value
            The expected start view.
        timeout
            The maximum time to wait for the start view to appear. Defaults to `None`.
        """
        # TODO-future; Composable expectations
        self.date_start.expect_startview(value, timeout=timeout)
        self.date_end.expect_startview(value, timeout=timeout)

    # weekstart: int = 0,
    def expect_weekstart(
        self,
        value: int | AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected week start.

        Parameters
        ----------
        value
            The expected week start.
        timeout
            The maximum time to wait for the week start to appear. Defaults to `None`.
        """
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
        """
        Asserts that the input element has the expected language.

        Parameters
        ----------
        value
            The expected language.
        timeout
            The maximum time to wait for the language to appear. Defaults to `None`.
        """
        # TODO-future; Composable expectations
        self.date_start.expect_language(value, timeout=timeout)
        self.date_end.expect_language(value, timeout=timeout)

    # separator: str = " to ",
    def expect_separator(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected separator.

        Parameters
        ----------
        value
            The expected separator.
        timeout
            The maximum time to wait for the separator to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_separator).to_have_text(value, timeout=timeout)

    # autoclose: bool = True,
    def expect_autoclose(
        self,
        value: Literal["true", "false"],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected autoclose value.

        Parameters
        ----------
        value
            The expected autoclose value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        # TODO-future; Composable expectations
        self.date_start.expect_autoclose(value, timeout=timeout)
        self.date_end.expect_autoclose(value, timeout=timeout)


class InputSubmitTextarea(
    _SetTextM,
    WidthContainerStyleM,
    _ExpectTextInputValueM,
    _ExpectPlaceholderAttrM,
    _ExpectRowsAttrM,
    UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_submit_textarea`."""

    loc_button: Locator
    """Playwright `Locator` for the submit button."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes the input submit textarea.

        Parameters
        ----------
        page
            The page where the input submit textarea is located.
        id
            The id of the input submit textarea.
        """
        super().__init__(
            page,
            id=id,
            loc=f"textarea#{id}.form-control",
        )
        self.loc_button = self.loc_container.locator(".bslib-submit-textarea-btn")

    def set(self, value: str, *, submit: bool = False, timeout: Timeout = None) -> None:
        """
        Sets the text value in the textarea.

        Parameters
        ----------
        value
            The text to set.
        submit
            Whether to click the submit button after setting the text. Defaults to `False`.
        timeout
            The maximum time to wait for the text to be set. Defaults to `None`.
        """
        set_text(self.loc, value, timeout=timeout)
        if submit:
            self.loc_button.click(timeout=timeout)

    def submit(self, *, timeout: Timeout = None) -> None:
        """
        Clicks the submit button.

        Parameters
        ----------
        timeout
            The maximum time to wait for the click. Defaults to `None`.
        """
        self.loc_button.click(timeout=timeout)

    def expect_data_needs_modifier(
        self, value: bool, *, timeout: Timeout = None
    ) -> None:
        """
        Expect the `data-needs-modifier` attribute to be present or absent.

        Parameters
        ----------
        value
            If `True`, expects the attribute to be present. If `False`, expects it to be absent.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc,
            "data-needs-modifier",
            value="" if value else None,
            timeout=timeout,
        )

    def expect_button_label(
        self, value: PatternOrStr, *, timeout: Timeout = None
    ) -> None:
        """
        Expect the submit button to have a specific label.

        Parameters
        ----------
        value
            The expected label text.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        playwright_expect(self.loc_button).to_contain_text(value, timeout=timeout)


class InputCodeEditor(
    WidthContainerStyleM,
    UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_code_editor`."""

    loc_editor: Locator
    """Playwright `Locator` for the inner code editor container."""
    loc_textarea: Locator
    """Playwright `Locator` for the textarea element."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes the input code editor.

        Parameters
        ----------
        page
            The page where the input code editor is located.
        id
            The id of the input code editor.
        """
        # The bslib-code-editor element itself is the container (no wrapper div)
        super().__init__(
            page,
            id=id,
            loc="xpath=.",
            loc_container=f"bslib-code-editor#{id}",
        )
        self.loc_editor = self.loc.locator(".code-editor")
        self.loc_textarea = self.loc_editor.locator("textarea")

    def _get_submit_modifier(self) -> str:
        """Get the appropriate modifier key for submit (Meta on Mac, Control elsewhere)."""
        return (
            "Meta"
            if self.page.evaluate("() => navigator.platform.includes('Mac')")
            else "Control"
        )

    def set(self, value: str, *, submit: bool = False, timeout: Timeout = None) -> None:
        """
        Sets the code value in the editor.

        Parameters
        ----------
        value
            The code to set.
        submit
            Whether to trigger a submit (Ctrl/Cmd+Enter) after setting the text.
            Defaults to `False`.
        timeout
            The maximum time to wait for the text to be set. Defaults to `None`.
        """
        set_text(self.loc_textarea, value, timeout=timeout)
        if submit:
            modifier = self._get_submit_modifier()
            self.loc_textarea.press(f"{modifier}+Enter", timeout=timeout)

    def submit(self, *, timeout: Timeout = None) -> None:
        """
        Triggers a submit by pressing Ctrl/Cmd+Enter.

        Parameters
        ----------
        timeout
            The maximum time to wait for the submit. Defaults to `None`.
        """
        modifier = self._get_submit_modifier()
        self.loc_textarea.press(f"{modifier}+Enter", timeout=timeout)

    def expect_value(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the value of the code editor to have a specific value.

        Parameters
        ----------
        value
            The expected value of the code editor.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        playwright_expect(self.loc_textarea).to_have_value(value, timeout=timeout)

    def expect_language(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the language attribute to have a specific value.

        Parameters
        ----------
        value
            The expected language (e.g., "python", "r", "javascript").
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "language", value=value, timeout=timeout
        )

    def expect_theme_light(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the light theme attribute to have a specific value.

        Parameters
        ----------
        value
            The expected light theme name.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "theme-light", value=value, timeout=timeout
        )

    def expect_theme_dark(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the dark theme attribute to have a specific value.

        Parameters
        ----------
        value
            The expected dark theme name.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "theme-dark", value=value, timeout=timeout
        )

    def expect_read_only(
        self,
        value: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the read-only state to have a specific value.

        Parameters
        ----------
        value
            Whether the editor should be read-only.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "readonly", value="true" if value else "false", timeout=timeout
        )

    def expect_line_numbers(
        self,
        value: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the line numbers visibility to have a specific value.

        Parameters
        ----------
        value
            Whether line numbers should be shown.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc,
            "line-numbers",
            value="true" if value else "false",
            timeout=timeout,
        )

    def expect_word_wrap(
        self,
        value: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the word wrap state to have a specific value.

        Parameters
        ----------
        value
            Whether word wrap should be enabled.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "word-wrap", value="true" if value else "false", timeout=timeout
        )

    def expect_tab_size(
        self,
        value: int | str,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the tab size to have a specific value.

        Parameters
        ----------
        value
            The expected tab size.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "tab-size", value=str(value), timeout=timeout
        )

    def expect_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expect the height style to have a specific value.

        Parameters
        ----------
        value
            The expected height value.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc, "height", value, timeout=timeout)
