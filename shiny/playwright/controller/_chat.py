from __future__ import annotations

from typing import Literal

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

from .._types import PatternOrStr, Timeout
from ._base import UiBase


class Chat(UiBase):
    """Controller for :func:`shiny.ui.chat`."""

    loc: Locator
    """
    Playwright `Locator` for the chat.
    """
    loc_messages: Locator
    """
    Playwright `Locator` for the chat messages.
    """
    loc_latest_message: Locator
    """
    Playwright `Locator` for the last message in the chat.
    """
    loc_input_container: Locator
    """
    Playwright `Locator` for the chat input container.
    """
    loc_input: Locator
    """
    Playwright `Locator` for the chat's <textarea> input.
    """
    loc_input_button: Locator
    """
    Playwright `Locator` for the chat's <button> input.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `Chat` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the chat.
        """
        super().__init__(
            page,
            id=id,
            loc=f"#{id}",
        )
        self.loc_messages = self.loc.locator("> shiny-chat-messages")
        self.loc_latest_message = self.loc_messages.locator("> :last-child")
        self.loc_input_container = self.loc.locator("> shiny-chat-input")
        self.loc_input = self.loc_input_container.locator("textarea")
        self.loc_input_button = self.loc_input_container.locator("button")

    def expect_latest_message(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the last message in the chat.

        Parameters
        ----------
        value
            The expected last message.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        # playwright_expect(self.loc_latest_message).to_have_text(value, timeout=timeout)
        playwright_expect(self.loc_latest_message).to_have_text(
            value, use_inner_text=True, timeout=timeout
        )

    def expect_messages(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the chat messages.

        Parameters
        ----------
        value
            The expected messages.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_messages).to_have_text(
            value, use_inner_text=True, timeout=timeout
        )

    def set_user_input(
        self,
        value: str,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Sets the user message in the chat.

        Parameters
        ----------
        value
            The message to send.
        timeout
            The maximum time to wait for the chat input to be visible and interactable. Defaults to `None`.
        """
        self.loc_input.type(value, timeout=timeout)

    def send_user_input(
        self, *, method: Literal["enter", "click"] = "enter", timeout: Timeout = None
    ) -> None:
        """
        Sends the user message in the chat.

        Parameters
        ----------
        method
            The method to send the user message. Defaults to `"enter"`.
        timeout
            The maximum time to wait for the chat input to be visible and interactable. Defaults to `None`.
        """
        if method == "enter":
            self.loc_input.press("Enter", timeout=timeout)
        else:
            self.loc_input_button.click(timeout=timeout)

    def expect_user_input(
        self, value: PatternOrStr, *, timeout: Timeout = None
    ) -> None:
        """
        Expects the user message in the chat.

        Parameters
        ----------
        value
            The expected user message.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_input).to_have_value(value, timeout=timeout)
