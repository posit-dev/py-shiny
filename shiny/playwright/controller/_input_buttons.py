from __future__ import annotations

import pathlib
import re
from typing import Literal, Optional

from playwright.sync_api import FilePayload, Locator, Page
from playwright.sync_api import expect as playwright_expect

# Import `shiny`'s typing extentions.
# Since this is a private file, tell pyright to ignore the import
from .._types import AttrValue, PatternOrStr, StyleValue, Timeout
from ..expect._internal import (
    expect_attribute_to_have_value as _expect_attribute_to_have_value,
)
from ..expect._internal import expect_style_to_have_value as _expect_style_to_have_value
from ._base import (
    InputActionBase,
    UiBase,
    UiWithLabel,
    WidthLocStlyeM,
    _expect_multiple,
)


class InputActionButton(
    WidthLocStlyeM,
    InputActionBase,
):
    """Controller for :func:`shiny.ui.input_action_button`."""

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initializes the input action button.

        Parameters
        ----------
        page
            The page where the input action button is located.
        id
            The id of the input action button.
        """
        super().__init__(
            page,
            id=id,
            loc=f'button[id="{id}"].action-button.shiny-bound-input',
        )

    def expect_disabled(self, value: bool, *, timeout: Timeout = None):
        """
        Expect the input action button to be disabled.

        Parameters
        ----------
        value
            The expected value of the `disabled` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "disabled", re.compile(".*") if value else None, timeout=timeout
        )


class InputBookmarkButton(
    InputActionButton,
):
    """Controller for :func:`shiny.ui.input_bookmark_button`."""

    def __init__(
        self,
        page: Page,
        id: str = "._bookmark_",
    ) -> None:
        """
        Initializes the input bookmark button.

        Parameters
        ----------
        page
            The page where the input bookmark button is located.
        id
            The id of the input bookmark button. Defaults to "._bookmark_".
        """
        super().__init__(
            page,
            id=id,
        )

    def expect_disabled(self, value: bool, *, timeout: Timeout = None):
        """
        Expect the input bookmark button to be disabled.

        Parameters
        ----------
        value
            The expected value of the `disabled` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        super().expect_disabled(value, timeout=timeout)


class InputDarkMode(UiBase):
    """Controller for :func:`shiny.ui.input_dark_mode`."""

    def __init__(
        self,
        page: Page,
        id: Optional[str] | None,
    ) -> None:
        """
        Initializes the input dark mode.

        Parameters
        ----------
        page
            The page where the input dark mode is located.
        id
            The id of the input dark mode.
        """
        id_selector = "" if id is None else f"#{id}"

        super().__init__(
            page,
            id="" if id is None else id,
            loc=f"bslib-input-dark-mode{id_selector}",
        )

    def click(self, *, timeout: Timeout = None):
        """
        Clicks the input dark mode.

        Parameters
        ----------
        timeout
            The maximum time to wait for the input dark mode to be clicked. Defaults to `None`.
        """
        self.loc.locator("button").click(timeout=timeout)
        return self

    def expect_mode(self, value: str, *, timeout: Timeout = None):
        """
        Expect the `mode` attribute of the input dark mode to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `mode` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "mode", value=value, timeout=timeout)
        self.expect_page_mode(value, timeout=timeout)
        return self

    def expect_page_mode(self, value: str, *, timeout: Timeout = None):
        """
        Expect the page to have a specific dark mode value.

        Parameters
        ----------
        value
            The expected value of the page's dark mode.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.page.locator("html"), "data-bs-theme", value=value, timeout=timeout
        )
        return self

    def expect_attribute(self, value: str, *, timeout: Timeout = None):
        """
        Expect the attribute named `attribute` of the input dark mode to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `attribute` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "attribute", value=value, timeout=timeout
        )
        return self


class InputTaskButton(
    WidthLocStlyeM,
    InputActionBase,
):
    """Controller for :func:`shiny.ui.input_task_button`."""

    # TODO-Karan: Test auto_reset functionality
    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initializes the input task button.

        Parameters
        ----------
        page
            The page where the input task button is located.
        id
            The id of the input task button.
        """
        super().__init__(
            page,
            id=id,
            loc=f"button#{id}.bslib-task-button.shiny-bound-input",
        )

    def expect_state(
        self,
        value: Literal["ready", "busy"] | str,
        *,
        timeout: Timeout = None,
    ):
        """
        Expect the state of the input task button to have a specific value.

        Parameters
        ----------
        value
            The expected value of the state of the input task button.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc.locator("> bslib-switch-inline"),
            name="case",
            value=value,
            timeout=timeout,
        )

    def expect_label(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expect the label of the input task button to have a specific value.

        Parameters
        ----------
        value
            The expected value of the label.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        self.expect_label_ready(value, timeout=timeout)

    def expect_label_ready(self, value: PatternOrStr, *, timeout: Timeout = None):
        """
        Expect the label of a ready input task button to have a specific value.

        Parameters
        ----------
        value
            The expected value of the label.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        self.expect_label_state("ready", value, timeout=timeout)

    def expect_label_busy(self, value: PatternOrStr, *, timeout: Timeout = None):
        """
        Expect the label of a busy input task button to have a specific value.

        Parameters
        ----------
        value
            The expected value of the label.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        self.expect_label_state("busy", value, timeout=timeout)

    def expect_label_state(
        self,
        state: str,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ):
        """
        Expect the label of the input task button to have a specific value in a specific state.

        Parameters
        ----------
        state
            The state of the input task button.
        value
            The expected value of the label.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        playwright_expect(
            self.loc.locator(f"> bslib-switch-inline > span[slot='{state}']")
        ).to_have_text(value, timeout=timeout)

    def expect_auto_reset(self, value: bool, timeout: Timeout = None):
        """
        Expect the `auto-reset` attribute of the input task button to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `auto-reset` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc,
            name="data-auto-reset",
            value="" if value else None,
            timeout=timeout,
        )


class InputActionLink(InputActionBase):
    """Controller for :func:`shiny.ui.input_action_link`."""

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initializes the input action link.

        Parameters
        ----------
        page
            The page where the input action link is located.
        id
            The id of the input action link.
        """
        super().__init__(
            page,
            id=id,
            loc=f"a#{id}.action-button.shiny-bound-input",
        )


class InputFile(
    # _ExpectPlaceholderAttrM,
    UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_file`."""

    loc_button: Locator
    """
    Playwright `Locator` of the button.
    """
    loc_file_display: Locator
    """
    Playwright `Locator` of the file display.
    """
    loc_progress: Locator
    """
    Playwright `Locator` of the progress bar.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initialize the InputFile.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The id of the file input.
        """
        super().__init__(
            page,
            id=id,
            loc=f"input[type=file]#{id}",
        )
        self.loc_button = self.loc_container.locator("label span.btn")
        self.loc_file_display = self.loc_container.locator("input[type=text]")
        self.loc_progress = self.loc_container.locator(".progress-bar")

    def set(
        self,
        file_path: (
            str
            | pathlib.Path
            | FilePayload
            | list[str | pathlib.Path]
            | list[FilePayload]
        ),
        *,
        timeout: Timeout = None,
        expect_complete_timeout: Timeout = 30 * 1000,
    ) -> None:
        """
        Set the file upload.

        Parameters
        ----------
        file_path
            The path to the file to upload.
        timeout
            The timeout for the action. Defaults to `None`.
        expect_complete_timeout
            The timeout for the expectation that the upload is complete. Defaults to `30 * 1000`.
        """
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        self.loc.set_input_files(file_path, timeout=timeout)
        if expect_complete_timeout is not None:
            self.expect_complete(timeout=expect_complete_timeout)

    # TODO-future: Let's make sure that if the upload errors out, expect_complete() fails.
    def expect_complete(
        self,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the file upload to be complete.

        Parameters
        ----------
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc_progress, "width", "100%", timeout=timeout)

    # TODO-future; Test multiple file upload
    def expect_multiple(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the `multiple` attribute to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `multiple` attribute.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_multiple(self.loc, value, timeout=timeout)

    def expect_accept(
        self,
        value: list[str] | AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `accept` attribute to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `accept` attribute.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        if isinstance(value, list):
            value = ",".join(value)
        _expect_attribute_to_have_value(self.loc, "accept", value, timeout=timeout)

    def expect_width(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expect the width of the input file to have a specific value.

        Parameters
        ----------
        value
            The expected value of the width.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc_container, "width", value, timeout=timeout)

    def expect_button_label(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the button label to have a specific value.

        Parameters
        ----------
        value
            The expected value of the button label.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        playwright_expect(self.loc_button).to_have_text(value, timeout=timeout)

    def expect_capture(
        self,
        value: Literal["environment", "user"] | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the `capture` attribute to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `capture` attribute.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc, "capture", value, timeout=timeout)

    def expect_placeholder(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        _expect_attribute_to_have_value(
            self.loc_file_display, "placeholder", value=value, timeout=timeout
        )
