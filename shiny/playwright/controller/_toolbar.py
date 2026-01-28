from __future__ import annotations

import re
from typing import Optional

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

from .._types import Timeout
from ..expect._internal import (
    expect_attribute_to_have_value as _expect_attribute_to_have_value,
)
from ._base import InputActionBase, UiBase


class ToolbarInputButton(InputActionBase):
    """
    Controller for :func:`shiny.ui.toolbar_input_button`.
    """

    loc_label: Locator
    """
    Playwright `Locator` for the button's label element.
    """
    loc_icon: Locator
    """
    Playwright `Locator` for the button's icon element.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initialize the toolbar input button controller.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The id of the toolbar button input.
        """
        super().__init__(
            page,
            id=id,
            loc=f'button[id="{id}"].bslib-toolbar-input-button.action-button',
        )
        self.loc_label = self.loc.locator(".bslib-toolbar-label")
        self.loc_icon = self.loc.locator(".bslib-toolbar-icon")

    def expect_label(
        self,
        value: str,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the label text of the toolbar button.

        Parameters
        ----------
        value
            The expected label text.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        playwright_expect(self.loc_label).to_have_text(value, timeout=timeout)

    def expect_icon(
        self,
        exists: bool = True,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the toolbar button to have an icon.

        Parameters
        ----------
        exists
            Whether the icon should exist.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        expected_count = 1 if exists else 0
        playwright_expect(self.loc_icon).to_have_count(expected_count, timeout=timeout)

    def expect_label_visible(
        self,
        visible: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the label to be visible or hidden.

        Parameters
        ----------
        visible
            Whether the label should be visible.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc_label,
            "hidden",
            None if visible else re.compile(".*"),
            timeout=timeout,
        )

    def expect_disabled(
        self,
        value: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the toolbar button to be disabled.

        Parameters
        ----------
        value
            Whether the button should be disabled.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc,
            "disabled",
            re.compile(".*") if value else None,
            timeout=timeout,
        )

    def expect_border(
        self,
        has_border: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the toolbar button to have a border.

        Parameters
        ----------
        has_border
            Whether the button should have a border.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        # border=True adds "border-1" class, border=False adds "border-0" class
        expected_class = "border-1" if has_border else "border-0"
        playwright_expect(self.loc).to_have_class(
            re.compile(f".*{expected_class}.*"), timeout=timeout
        )


class ToolbarInputSelect(UiBase):
    """
    Controller for :func:`shiny.ui.toolbar_input_select`.
    """

    loc_select: Locator
    """
    Playwright `Locator` for the internal select element.
    """
    loc_label: Locator
    """
    Playwright `Locator` for the label element.
    """
    loc_icon: Locator
    """
    Playwright `Locator` for the icon element.
    """
    loc_choices: Locator
    """
    Playwright `Locator` for all option elements.
    """
    loc_selected: Locator
    """
    Playwright `Locator` for the currently selected option.
    """
    loc_choice_groups: Locator
    """
    Playwright `Locator` for optgroup elements.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initialize the toolbar select input controller.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The id of the toolbar select input.
        """
        super().__init__(
            page,
            id=id,
            loc=f"div#{id}.bslib-toolbar-input-select",
        )
        self.loc_select = self.loc.locator(f"select#{id}-select")
        self.loc_label = self.loc.locator("label .bslib-toolbar-label")
        self.loc_icon = self.loc.locator("label .bslib-toolbar-icon")
        self.loc_choices = self.loc_select.locator("option")
        self.loc_selected = self.loc_select.locator("option:checked")
        self.loc_choice_groups = self.loc_select.locator("optgroup")

    def set(
        self,
        value: str,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Set the selected value of the toolbar select input.

        Parameters
        ----------
        value
            The value to select.
        timeout
            The maximum time to wait for the selection to be set. Defaults to `None`.
        """
        self.loc_select.select_option(value=value, timeout=timeout)

    def expect_label(
        self,
        value: str,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the label text of the toolbar select.

        Parameters
        ----------
        value
            The expected label text.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        playwright_expect(self.loc_label).to_have_text(value, timeout=timeout)

    def expect_icon(
        self,
        exists: bool = True,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the toolbar select to have an icon.

        Parameters
        ----------
        exists
            Whether the icon should exist.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        expected_count = 1 if exists else 0
        playwright_expect(self.loc_icon).to_have_count(expected_count, timeout=timeout)

    def expect_label_visible(
        self,
        visible: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the label to be visible or hidden.

        Parameters
        ----------
        visible
            Whether the label should be visible.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        if visible:
            playwright_expect(self.loc_label).not_to_have_class(
                re.compile(".*visually-hidden.*"), timeout=timeout
            )
        else:
            playwright_expect(self.loc_label).to_have_class(
                re.compile(".*visually-hidden.*"), timeout=timeout
            )

    def expect_choices(
        self,
        choices: list[str],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the available choices of the toolbar select.

        Parameters
        ----------
        choices
            The expected list of choice values.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        if len(choices) == 0:
            playwright_expect(self.loc_choices).to_have_count(0, timeout=timeout)
            return

        # Get all option values and compare
        playwright_expect(self.loc_choices).to_have_count(len(choices), timeout=timeout)
        for i, expected_value in enumerate(choices):
            playwright_expect(self.loc_choices.nth(i)).to_have_attribute(
                "value", expected_value, timeout=timeout
            )

    def expect_selected(
        self,
        value: str,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the currently selected value of the toolbar select.

        Parameters
        ----------
        value
            The expected selected value.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        playwright_expect(self.loc_select).to_have_value(value, timeout=timeout)

    def expect_choice_groups(
        self,
        labels: list[str],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the optgroup labels of the toolbar select.

        Parameters
        ----------
        labels
            The expected list of optgroup labels.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        if len(labels) == 0:
            playwright_expect(self.loc_choice_groups).to_have_count(
                0, timeout=timeout
            )
            return

        playwright_expect(self.loc_choice_groups).to_have_text(labels, timeout=timeout)
