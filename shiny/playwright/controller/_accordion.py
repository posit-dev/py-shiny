from __future__ import annotations

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

from .._types import PatternOrStr, StyleValue, Timeout
from ..expect import expect_not_to_have_class
from ..expect._internal import expect_class_to_have_value as _expect_class_to_have_value
from ..expect._internal import expect_style_to_have_value as _expect_style_to_have_value
from ._base import UiWithContainer, WidthLocM
from ._expect import expect_locator_values_in_list


class AccordionPanel(
    WidthLocM,
    UiWithContainer,
):
    """
    Controller for :func:`shiny.ui.accordion_panel`.
    """

    loc_label: Locator
    """
    Playwright `Locator` for the accordion panel's label.
    """
    loc_icon: Locator
    """
    Playwright `Locator` for the accordion panel's icon.
    """
    loc_body: Locator
    """
    Playwright `Locator` for the accordion panel's body.
    """
    loc_header: Locator
    """
    Playwright `Locator` for the accordion panel's header.
    """
    # loc_body_visible: Locator
    # """
    # Playwright `Locator` for the visible accordion panel body
    # """

    def __init__(self, page: Page, id: str, data_value: str) -> None:
        """
        Initializes a new instance of the `AccordionPanel` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the accordion panel.
        data_value
            The data value of the accordion panel.
        """
        super().__init__(
            page,
            id=id,
            loc=f"> div.accordion-item[data-value='{data_value}']",
            loc_container=f"div#{id}.accordion.shiny-bound-input",
        )

        self.loc_label = self.loc.locator(
            "> .accordion-header > .accordion-button > .accordion-title"
        )

        self.loc_icon = self.loc.locator(
            "> .accordion-header > .accordion-button > .accordion-icon"
        )

        self.loc_body = self.loc.locator("> .accordion-collapse")
        self.loc_header = self.loc.locator("> .accordion-header")
        self._loc_body_visible = self.loc.locator("> .accordion-collapse.show")

    def expect_label(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the accordion panel label to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the label to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_label).to_have_text(value, timeout=timeout)

    def expect_body(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Expects the accordion panel body to have the specified text.

        Parameters
        ----------
        value
            The expected text pattern or string.
        timeout
            The maximum time to wait for the body to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_body).to_have_text(value, timeout=timeout)

    def expect_icon(self, exists: bool, *, timeout: Timeout = None) -> None:
        """
        Expects the accordion panel icon to exist or not.

        Parameters
        ----------
        exists
            `True` if the icon is expected to exist, `False` otherwise.
        timeout
            The maximum time to wait for the icon to appear. Defaults to `None`.
        """
        icon_child_loc = self.loc_icon.locator("> *")
        if exists:
            playwright_expect(icon_child_loc).not_to_have_count(0, timeout=timeout)
        else:
            playwright_expect(icon_child_loc).to_have_count(0, timeout=timeout)

    def expect_open(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expects the accordion panel to be open or closed.

        Parameters
        ----------
        value
            `True` if the accordion panel is expected to be open, `False` otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc_body,
            "show",
            has_class=value,
            timeout=timeout,
        )

    # user sends value of Open: true | false
    def set(self, open: bool, *, timeout: Timeout = None) -> None:
        """
        Sets the state of the control to open or closed.

        Parameters
        ----------
        open
            `True` to open the accordion panel, False to close it.
        timeout
            The maximum time to wait for the control to be visible and interactable. Defaults to `None`.
        """
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        expect_not_to_have_class(self.loc_body, "collapsing", timeout=timeout)
        if self._loc_body_visible.count() != int(open):
            self._toggle(timeout=timeout)

    def _toggle(self, *, timeout: Timeout = None) -> None:
        """
        Toggles the state of the control.

        Parameters
        ----------
        timeout
            The maximum time to wait for the control to be visible and interactable. Defaults to `None`.
        """
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        self.loc_header.click(timeout=timeout)


class Accordion(
    WidthLocM,
    UiWithContainer,
):
    """Controller for :func:`shiny.ui.accordion`."""

    loc: Locator
    """
    Playwright `Locator` for each accordion items.
    """
    loc_container: Locator
    """
    Playwright `Locator` for the accordion container.
    """
    # loc_open: Locator
    # """
    # `Locator` for the open accordion panel
    # """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `Accordion` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the accordion.
        """
        super().__init__(
            page,
            id=id,
            loc="> div.accordion-item",
            loc_container=f"div#{id}.accordion.shiny-bound-input",
        )
        # self.loc_open = self.loc.locator(
        #   "xpath=.",
        #     # Simple approach as position is not needed
        #     has=page.locator(
        #         "> div.accordion-collapse.show",
        #     ),
        # )

    def expect_height(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expects the accordion to have the specified height.

        Parameters
        ----------
        value
            The expected height.
        timeout
            The maximum time to wait for the height to be visible and interactable. Defaults to `None`.
        """
        _expect_style_to_have_value(
            self.loc_container, "height", value, timeout=timeout
        )

    def expect_width(self, value: StyleValue, *, timeout: Timeout = None) -> None:
        """
        Expects the accordion to have the specified width.

        Parameters
        ----------
        value
            The expected width.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc_container, "width", value, timeout=timeout)

    def expect_open(
        self,
        value: list[PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
        expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type=self.page.locator(
                "> div.accordion-item",
                has=self.page.locator("> div.accordion-collapse.show"),
            ),
            # el_type="> div.accordion-item:has(> div.accordion-collapse.show)",
            arr_name="value",
            arr=value,
            key="data-value",
            timeout=timeout,
            alt_verify=True,
        )

    def expect_panels(
        self,
        value: list[PatternOrStr],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the accordion to have the specified panels.

        Parameters
        ----------
        value
            The expected panels.
        timeout
            The maximum time to wait for the panels to be visible and interactable. Defaults to `None`.
        """
        expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="> div.accordion-item",
            arr_name="value",
            arr=value,
            key="data-value",
            timeout=timeout,
            alt_verify=True,
        )

    def set(
        self,
        open: str | list[str],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Sets the state of the accordion panel.

        Parameters
        ----------
        open
            The open accordion panel(s).
        timeout
            The maximum time to wait for the accordion panel to be visible and interactable. Defaults to `None`.
        """
        if isinstance(open, str):
            open = [open]

        # TODO-future: XOR on the next open state and the current open state
        for i in range(self.loc.count()):
            el_loc = self.loc.nth(i)
            el_loc.element_handle().wait_for_element_state(
                state="visible", timeout=timeout
            )
            el_loc.scroll_into_view_if_needed(timeout=timeout)

            elem_value = el_loc.get_attribute("data-value")
            if elem_value is None:
                raise ValueError(
                    "Accordion panel does not have a `data-value` attribute"
                )
            self.accordion_panel(elem_value).set(elem_value in open, timeout=timeout)

    def expect_class(
        self,
        class_name: str,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the accordion to have the specified class.

        Parameters
        ----------
        class_name
            The class name to expect.
        timeout
            The maximum time to wait for the class to appear. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc_container,
            class_name,
            has_class=True,
            timeout=timeout,
        )

    def expect_multiple(
        self,
        value: bool,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the accordion to be multiple or not.

        Parameters
        ----------
        value
            `True` if the accordion is expected to be multiple, `False` otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc_container,
            "autoclose",
            has_class=not value,
            timeout=timeout,
        )

    def accordion_panel(
        self,
        data_value: str,
    ) -> AccordionPanel:
        """
        Returns the accordion panel (:class:`~shiny.playwright.controls.AccordionPanel`)
        with the specified data value.

        Parameters
        ----------
        data_value
            The data value of the accordion panel.
        """
        return AccordionPanel(self.page, self.id, data_value)
