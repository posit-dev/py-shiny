from __future__ import annotations

import platform
from typing import Literal, Protocol

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

from ...render._data_frame import ColumnFilter, ColumnSort
from .._types import AttrValue, ListPatternOrStr, PatternOrStr, StyleValue, Timeout
from ..expect import expect_not_to_have_class, expect_to_have_class
from ..expect._internal import (
    expect_attribute_to_have_value as _expect_attribute_to_have_value,
)
from ..expect._internal import expect_class_to_have_value as _expect_class_to_have_value
from ..expect._internal import expect_style_to_have_value as _expect_style_to_have_value
from ._base import InitLocator, OutputBaseP, UiWithContainer


class _OutputBase:
    """
    Base class for output controls.
    """

    id: str
    """
    The ID of the output control.
    """
    loc: Locator
    """
    Playwright `Locator` of the output control.
    """
    page: Page
    """
    Playwright `Page` of the Shiny app.
    """

    def __init__(
        self,
        page: Page,
        *,
        id: str,
        loc: InitLocator,
    ) -> None:
        self.page = page
        self.id = id

        if isinstance(loc, str):
            loc = page.locator(loc)
        self.loc = loc

    @property
    # TODO; Return type
    def expect(self):
        return playwright_expect(self.loc)


class _OutputTextValue(_OutputBase):
    # cls = "shiny-text-output" + (" noplaceholder" if not placeholder else "")
    # return tags.pre(id=resolve_id(id), class_=cls)

    def expect_value(
        self,
        value: PatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the output has the expected value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        """Note this function will trim value and output text value before comparing them"""
        self.expect.to_have_text(value, timeout=timeout)


class _OutputContainerP(OutputBaseP, Protocol):
    def expect_container_tag(
        self: OutputBaseP,
        value: Literal["span", "div"] | str,
        *,
        timeout: Timeout = None,
    ) -> None: ...


class _OutputContainerM:
    def expect_container_tag(
        self: OutputBaseP,
        value: Literal["span", "div"] | str,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the output has the expected container tag.

        Parameters
        ----------
        value
            The expected container tag.
        timeout
            The maximum time to wait for the container tag to appear. Defaults to `None`.
        """
        loc = self.loc.locator(f"xpath=self::{value}")
        playwright_expect(loc).to_have_count(1, timeout=timeout)


class _OutputInlineContainerM(_OutputContainerM):
    def expect_inline(
        self: _OutputContainerP,
        value: bool = False,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the output is inline.

        Parameters
        ----------
        value
            Whether the output is inline.
        timeout
            The maximum time to wait for the output to appear. Defaults to `None`.
        """
        tag_name = "span" if value else "div"
        self.expect_container_tag(tag_name, timeout=timeout)


class OutputText(
    _OutputInlineContainerM,
    _OutputTextValue,
):
    """Controller for :func:`shiny.ui.output_text`."""

    loc: Locator
    """
    Playwright `Locator` of the text output.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initializes a text output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the text output.
        """
        super().__init__(page, id=id, loc=f"#{id}.shiny-text-output")

    def get_value(self, *, timeout: Timeout = None) -> str:
        """
        Gets the text value of the output.

        Parameters
        ----------
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        return self.loc.inner_text(timeout=timeout)


class OutputCode(_OutputTextValue):
    """Controller for :func:`shiny.ui.output_code`."""

    loc: Locator
    """
    Playwright `Locator` of the code output.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a code output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the code output.
        """
        super().__init__(page, id=id, loc=f"pre#{id}.shiny-text-output")

    def expect_has_placeholder(
        self,
        value: bool = False,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the code output has the expected placeholder.

        Parameters
        ----------
        value
            Whether the code output has a placeholder.
        timeout
            The maximum time to wait for the placeholder to appear. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc,
            class_="noplaceholder",
            has_class=not value,
            timeout=timeout,
        )


class OutputTextVerbatim(_OutputTextValue):
    """Controller for :func:`shiny.ui.output_text_verbatim`."""

    loc: Locator
    """
    Playwright `Locator` of the verbatim text output.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a verbatim text output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the verbatim text output.
        """
        super().__init__(page, id=id, loc=f"pre#{id}.shiny-text-output")

    def expect_has_placeholder(
        self,
        value: bool = False,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the verbatim text output has the expected placeholder.

        Parameters
        ----------
        value
            Whether the verbatim text output has a placeholder.
        timeout
            The maximum time to wait for the placeholder to appear. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc,
            class_="noplaceholder",
            has_class=not value,
            timeout=timeout,
        )


class _OutputImageBase(_OutputInlineContainerM, _OutputBase):

    loc_img: Locator
    """
    Playwright `Locator` of the image.
    """

    def __init__(
        self,
        page: Page,
        id: str,
        loc_classes: str = "",
    ) -> None:
        """
        Initializes an image output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the image.
        loc_classes
            Additional classes to locate the image. Defaults to "".
        """
        super().__init__(
            page,
            id=id,
            loc=f"#{id}.shiny-image-output{loc_classes}",
        )
        self.loc_img = self.loc.locator("img")

    def expect_height(
        self,
        value: StyleValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the image has the expected height.

        Parameters
        ----------
        value
            The expected height.
        timeout
            The maximum time to wait for the height to appear. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc, "height", value, timeout=timeout)

    def expect_width(
        self,
        value: StyleValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the image has the expected width.

        Parameters
        ----------
        value
            The expected width.
        timeout
            The maximum time to wait for the width to appear. Defaults to `None`.
        """
        _expect_style_to_have_value(self.loc, "width", value, timeout=timeout)

    def expect_img_src(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the image has the expected src.

        Parameters
        ----------
        value
            The expected src.
        timeout
            The maximum time to wait for the src to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc_img, "src", value, timeout=timeout)

    def expect_img_width(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the image has the expected width.

        Parameters
        ----------
        value
            The expected width.
        timeout
            The maximum time to wait for the width to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc_img, "width", value, timeout=timeout)

    def expect_img_height(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the image has the expected height.

        Parameters
        ----------
        value
            The expected height.
        timeout
            The maximum time to wait for the height to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc_img, "height", value, timeout=timeout)

    def expect_img_alt(
        self,
        value: AttrValue,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the image has the expected alt text.

        Parameters
        ----------
        value
            The expected alt text.
        timeout
            The maximum time to wait for the alt text to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(self.loc_img, "alt", value, timeout=timeout)

    # def expect_img_style(
    #     self,
    #     value: AttrValue,
    #     *,
    #     timeout: Timeout = None,
    # ) -> None:
    #     expect_attr(self.loc_img, "style", value, timeout=timeout)


class OutputImage(_OutputImageBase):
    """Controller for :func:`shiny.ui.output_image`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes an image output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the image.
        """
        super().__init__(page, id=id)


class OutputPlot(_OutputImageBase):
    """Controller for :func:`shiny.ui.output_plot`."""

    loc: Locator
    """
    Playwright `Locator` of the plot output.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a plot output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the plot.
        """
        super().__init__(page, id=id, loc_classes=".shiny-plot-output")


class OutputUi(_OutputInlineContainerM, _OutputBase):
    """Controller for :func:`shiny.ui.output_ui`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a UI output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the UI output.
        """
        super().__init__(page, id=id, loc=f"#{id}")

    # TODO-future; Should we try verify that `recalculating` class is not present? Do this for all outputs!
    def expect_empty(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Asserts that the output is empty.

        Parameters
        ----------
        value
            Whether the output is empty.
        timeout
            The maximum time to wait for the output to be empty. Defaults to `None`.
        """
        if value:
            self.expect.to_be_empty(timeout=timeout)
        else:
            self.expect.not_to_be_empty(timeout=timeout)


class OutputTable(_OutputBase):
    """Controller for :func:`shiny.ui.output_table`."""

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a table output.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the table.
        """
        super().__init__(page, id=id, loc=f"#{id}")

    def expect_cell(
        self,
        value: PatternOrStr,
        row: int,
        col: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the table cell has the expected text.

        Parameters
        ----------
        value
            The expected text in the cell.
        row
            The row number.
        col
            The column number.
        timeout
            The maximum time to wait for the text to appear. Defaults to `None`.
        """
        if not isinstance(row, int):
            raise TypeError("`row` must be an integer")
        if not isinstance(col, int):
            raise TypeError("`col` must be an integer")
        playwright_expect(
            self.loc.locator(
                f"xpath=./table/tbody/tr[{row}]/td[{col}] | ./table/tbody/tr[{row}]/th[{col}]"
            )
        ).to_have_text(value, timeout=timeout)

    def expect_column_labels(
        self,
        value: ListPatternOrStr | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the table has the expected column labels.

        Parameters
        ----------
        value
            The expected column labels. If None, it asserts that the table has no column labels.
        timeout
            The maximum time to wait for the column labels to appear. Defaults to `None`.
        """
        if isinstance(value, list) and len(value) == 0:
            value = None

        if value is None:
            playwright_expect(
                self.loc.locator("xpath=./table/thead/tr/th")
            ).to_have_count(0, timeout=timeout)
        else:
            playwright_expect(
                self.loc.locator("xpath=./table/thead/tr/th")
            ).to_have_text(value, timeout=timeout)

    def expect_column_text(
        self,
        col: int,
        # Can't use `None` as we don't know how many rows exist
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the column has the expected text.

        Parameters
        ----------
        col
            The column number.
        value
            The expected text in the column.
        timeout
            The maximum time to wait for the text to appear. Defaults to `None`.
        """
        if not isinstance(col, int):
            raise TypeError("`col` must be an integer")
        playwright_expect(
            self.loc.locator(f"xpath=./table/tbody/tr/td[{col}]")
        ).to_have_text(
            value,
            timeout=timeout,
        )

    def expect_ncol(
        self,
        value: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the table has the expected number of columns.

        Parameters
        ----------
        value
            The expected number of columns in the table.
        timeout
            The maximum time to wait for the table to have the expected number of columns. Defaults to `None`.
        """
        playwright_expect(
            # self.loc.locator("xpath=./table/thead/tr[1]/(td|th)")
            self.loc.locator("xpath=./table/thead/tr[1]/td | ./table/thead/tr[1]/th")
        ).to_have_count(
            value,
            timeout=timeout,
        )

    def expect_nrow(
        self,
        value: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the table has the expected number of rows.

        Parameters
        ----------
        value
            The expected number of rows in the table.
        timeout
            The maximum time to wait for the table to have the expected number of rows. Defaults to `None`.
        """
        playwright_expect(self.loc.locator("xpath=./table/tbody/tr")).to_have_count(
            value,
            timeout=timeout,
        )


class OutputDataFrame(UiWithContainer):
    """
    Controller for :func:`shiny.ui.output_data_frame`.
    """

    loc_container: Locator
    """
    Playwright `Locator` for the data frame container.
    """
    loc: Locator
    """
    Playwright `Locator` for the data frame.
    """
    loc_head: Locator
    """
    Playwright `Locator` for the head of the data frame table.
    """
    loc_body: Locator
    """
    Playwright `Locator` for the body of the data frame table.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes a new instance of the `OutputDataFrame` class.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The ID of the data frame.
        """
        super().__init__(
            page,
            id=id,
            loc_container=f"#{id}.html-fill-item",
            loc="> div > div.shiny-data-grid",
        )
        self.loc_table = self.loc.locator("> table")
        self.loc_head = self.loc_table.locator("> thead")
        self.loc_body = self.loc_table.locator("> tbody")
        self.loc_column_filter = self.loc_head.locator(
            "> tr.filters > th:not(.table-corner)"
        )
        self.loc_column_label = self.loc_head.locator(
            "> tr:not(.filters) > th:not(.table-corner)"
        )

    def cell_locator(self, row: int, col: int) -> Locator:
        """
        Returns the locator for a specific cell in the data frame.

        Parameters
        ----------
        row
            The row number of the cell.
        col
            The column number of the cell.
        """

        return (
            # Find the direct row
            self.loc_body.locator(f"> tr[data-index='{row}']")
            # Find all direct td's and th's (these are independent sets)
            .locator("> td, > th")
            # Remove all results that contain the `row-number` class
            .locator(
                # self
                "xpath=.",
                has=self.page.locator(
                    "xpath=self::*[not(contains(@class, 'row-number'))]"
                ),
            )
            # Return the first result
            .nth(col)
        )

    # TODO-barret; Should this be called `expect_row_count()`?
    def expect_nrow(self, value: int, *, timeout: Timeout = None):
        """
        Expects the number of rows in the data frame.

        Parameters
        ----------
        value
            The expected number of rows.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_table).to_have_attribute(
            "aria-rowcount",
            str(value),
            timeout=timeout,
        )

    def expect_selected_num_rows(self, value: int, *, timeout: Timeout = None):
        """
        Expects the number of selected rows in the data frame.

        Parameters
        ----------
        value
            The expected number of selected rows.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(
            self.loc_body.locator("tr[aria-selected=true]")
        ).to_have_count(value, timeout=timeout)

    def expect_selected_rows(self, rows: list[int], *, timeout: Timeout = None):
        """
        Expects the specified rows to be selected.

        Parameters
        ----------
        rows
            The row numbers.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        # * given container...
        # * Add that container has all known rows
        # * Verify that selected row count is of size N
        big_loc = self.loc_body
        assert len(rows) > 0
        for row in rows:
            big_loc = big_loc.locator(
                "xpath=.",  # return "self"
                has=self.page.locator(
                    f"> tr[data-index='{row}'][aria-selected='true']"
                ),
            )

        try:
            playwright_expect(
                big_loc.locator("> tr[aria-selected='true']")
            ).to_have_count(len(rows), timeout=timeout)
        except AssertionError as e:
            # Debug expections

            # Expecting container to exist (count = 1)
            playwright_expect(self.loc_body).to_have_count(1, timeout=timeout)

            for row in rows:
                # Expecting item `{item}` to exist in container
                # Perform exact matches on strings.
                playwright_expect(
                    # Simple approach as position is not needed
                    self.loc_body.locator(
                        f"> tr[aria-selected='true'][data-index='{row}']",
                    )
                ).to_have_count(1, timeout=timeout)

            # Could not find the reason why. Raising the original error.
            raise e

    def _expect_row_focus_state(
        self, in_focus: bool = True, *, row: int, timeout: Timeout = None
    ):
        """
        Expects the focus state of the specified row.

        Parameters
        ----------
        row
            The row number.
        in_focus
            `True` if the row is expected to be in focus, `False` otherwise.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if in_focus:
            playwright_expect(
                self.loc_body.locator(f"> tr[data-index='{row}']")
            ).to_be_focused(timeout=timeout)
        else:
            playwright_expect(
                self.loc_body.locator(f"> tr[data-index='{row}']")
            ).not_to_be_focused(timeout=timeout)

    def expect_cell(
        self,
        value: PatternOrStr,
        *,
        row: int,
        col: int,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the cell in the data frame to have the specified text.

        Parameters
        ----------
        value
            The expected text in the cell.
        row
            The row number of the cell.
        col
            The column number of the cell.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if not isinstance(row, int):
            raise TypeError("`row` must be an integer.")
        if not isinstance(col, int):
            raise TypeError("`col` must be an integer.")
        self._cell_scroll_if_needed(row=row, col=col, timeout=timeout)
        playwright_expect(self.cell_locator(row, col)).to_have_text(
            value, timeout=timeout
        )

    def expect_column_labels(
        self,
        value: ListPatternOrStr | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the column labels in the data frame.

        Parameters
        ----------
        value
            The expected column labels.

            Note: None if the column labels are expected to not exist.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if isinstance(value, list) and len(value) == 0:
            value = None

        if value is None:
            playwright_expect(self.loc_column_label).to_have_count(0, timeout=timeout)
        else:
            playwright_expect(self.loc_column_label).to_have_text(
                value, timeout=timeout
            )

    def _cell_scroll_if_needed(self, *, row: int, col: int, timeout: Timeout):
        """
        Scrolls the cell into view if needed.

        Parameters
        ----------
        row
            The row number of the cell.
        col
            The column number of the cell.
        timeout
            The maximum time to wait for the action to complete.
        """
        # Check first and last row data-index and make sure `row` is included

        cell = self.cell_locator(row=row, col=col)

        # Scroll down if top number is larger
        while not cell.is_visible(timeout=timeout):
            first_row = self.loc_body.locator("> tr[data-index]").first
            first_row_index = first_row.get_attribute("data-index")
            if first_row_index is None:
                break
            if int(first_row_index) >= row:
                first_row.scroll_into_view_if_needed(timeout=timeout)
            else:
                # First row index is lower than `row`
                break
        # Scroll up if bottom number is smaller
        while not cell.is_visible(timeout=timeout):
            last_row = self.loc_body.locator("> tr[data-index]").last
            last_row_index = last_row.get_attribute("data-index")
            if last_row_index is None:
                break
            if int(last_row_index) <= row:
                last_row.scroll_into_view_if_needed(timeout=timeout)
            else:
                # Last row index is higher than `row`
                break
        cell.scroll_into_view_if_needed(timeout=timeout)

    def _expect_column_label(
        self,
        value: ListPatternOrStr,
        *,
        col: int,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the text in the specified column of the data frame.

        Parameters
        ----------
        value
            The expected text in the column.
        col
            The column number.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if not isinstance(col, int):
            raise TypeError("`col` must be an integer.")
        # It's zero based, nth(0) selects the first element.
        playwright_expect(self.loc_column_label.nth(col - 1)).to_have_text(
            value,
            timeout=timeout,
        )

    def expect_ncol(
        self,
        value: int,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the number of columns in the data frame.

        Parameters
        ----------
        value
            The expected number of columns.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.loc_column_label).to_have_count(
            value,
            timeout=timeout,
        )

    def expect_cell_class(
        self,
        value: str,
        *,
        row: int,
        col: int,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the class of the cell

        Parameters
        ----------
        value
            The expected class of the cell.
        row
            The row number of the cell.
        col
            The column number of the cell.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        expect_to_have_class(
            self.cell_locator(row=row, col=col),
            value,
            timeout=timeout,
        )

    def select_rows(
        self,
        value: list[int],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Selects the rows in the data frame.

        Parameters
        ----------
        value
            The list of row numbers to select.
        timeout
            The maximum time to wait for the action to complete. Defaults to `None`.
        """
        if len(value) > 1:
            value = sorted(value)
            # check if the items in the row contain all numbers from index 0 to index -1
            if value == list(range(value[0], value[-1] + 1)):
                self.page.keyboard.down("Shift")
                self.cell_locator(row=value[0], col=0).click(timeout=timeout)
                self.cell_locator(row=value[-1], col=0).click(timeout=timeout)
                self.page.keyboard.up("Shift")
            else:
                # if operating system is MacOs use Meta (Cmd) else use Ctrl key
                if platform.system() == "Darwin":
                    self.page.keyboard.down("Meta")
                else:
                    self.page.keyboard.down("Control")
                for row in value:
                    self._cell_scroll_if_needed(row=row, col=0, timeout=timeout)
                    self.cell_locator(row=row, col=0).click(timeout=timeout)
                if platform.system() == "Darwin":
                    self.page.keyboard.up("Meta")
                else:
                    self.page.keyboard.up("Control")
        else:
            self.cell_locator(row=value[0], col=0).click(timeout=timeout)

    def expect_class_state(
        self,
        value: str,
        *,
        row: int,
        col: int,
        timeout: Timeout = None,
    ):
        """
        Expects the state of the class in the data frame.

        Parameters
        ----------
        value
            The expected state of the class.
        row
            The row number of the cell.
        col
            The column number of the cell.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        if value == "ready":
            playwright_expect(self.cell_locator(row=row, col=col)).not_to_have_class(
                "cell-edit-editing", timeout=timeout
            )
        elif value == "editing":
            self.expect_cell_class(
                "cell-edit-editing",
                row=row,
                col=col,
                timeout=timeout,
            )
        elif value == "saving":
            self.expect_cell_class(
                "cell-edit-saving",
                row=row,
                col=col,
                timeout=timeout,
            )
        elif value == "failure":
            self.expect_cell_class(
                "cell-edit-failure",
                row=row,
                col=col,
                timeout=timeout,
            )
        elif value == "success":
            self.expect_cell_class(
                "cell-edit-success",
                row=row,
                col=col,
                timeout=timeout,
            )
        else:
            raise ValueError(
                "Invalid state. Select one of 'success', 'failure', 'saving', 'editing', 'ready'"
            )

    def _edit_cell_no_save(
        self,
        text: str,
        *,
        row: int,
        col: int,
        timeout: Timeout = None,
    ) -> None:
        """
        Edits the cell in the data frame.

        Parameters
        ----------
        value
            The value to edit in the cell.
        row
            The row number of the cell.
        col
            The column number of the cell.
        timeout
            The maximum time to wait for the action to complete. Defaults to `None`.
        """
        cell = self.cell_locator(row=row, col=col)

        self._cell_scroll_if_needed(row=row, col=col, timeout=timeout)
        cell.dblclick(timeout=timeout)
        cell.locator("> textarea").fill(text)

    def set_sort(
        self,
        sort: int | ColumnSort | list[int | ColumnSort] | None,
        *,
        timeout: Timeout = None,
    ):
        """
        Set or modify the sorting of columns in a table or grid component.
        This method allows setting single or multiple column sorts, or resetting the sort order.

        Parameters
        ----------
        sort
            The sorting configuration to apply. Can be one of the following:
                * `int`: Index of the column to sort by (ascending order by default).
                * `ColumnSort`: A dictionary specifying a single column sort with 'col' and 'desc' keys.
                * `list[int | ColumnSort]`: A list of ints or dictionaries for multi-column sorting.
                * `None`: No sorting applied (not implemented in the current code).

            If a `desc` values is provided within your `ColumnSort` shaped dictionary, then the direction will be set to that value. If no `desc` value is provided, the column will be sorted in the default sorting order.
        timeout
            The maximum time to wait for the action to complete. Defaults to `None`.
        """

        def click_loc(loc: Locator, *, shift: bool = False):
            clickModifier: list[Literal["Shift"]] | None = (
                ["Shift"] if bool(shift) else None
            )
            loc.click(
                timeout=timeout,
                modifiers=clickModifier,
            )
            # Wait for arrows to react a little bit
            # This could possible be changed to a `wait_for_change`, but 150ms should be fine
            self.page.wait_for_timeout(150)

        # Reset arrow sorting by clicking on the arrows until none are found
        sortingArrows = self.loc_column_label.locator("svg.sort-arrow")
        while sortingArrows.count() > 0:
            click_loc(sortingArrows.first)

        # Quit early if no sorting is needed
        if sort is None:
            return

        if isinstance(sort, int) | isinstance(sort, dict) and not isinstance(
            sort, list
        ):
            sort = [sort]

        if not isinstance(sort, list):
            raise ValueError(
                "Invalid sort value. Must be an int, ColumnSort, list[ColumnSort], or None."
            )

        # For every sorting info...
        for sort_info, i in zip(sort, range(len(sort))):
            # TODO-barret-future; assert column does not have `cell-html` class
            shift = i > 0

            if isinstance(sort_info, int):
                sort_info = {"col": sort_info}

            # Verify ColumnSortInfo
            assert isinstance(
                sort_info, dict
            ), f"Invalid sort value at position {i}. Must be an int, ColumnSort, list[ColumnSort], or None."
            assert (
                "col" in sort_info
            ), f"Column index (`col`) at position {i} is required for sorting."

            sort_col = self.loc_column_label.nth(sort_info["col"])
            expect_not_to_have_class(sort_col, "header-html")

            # If no `desc` key is found, click the column to sort and move on
            if "desc" not in sort_info:
                click_loc(sort_col, shift=shift)
                continue

            # "desc" in sort_info
            desc_val = bool(sort_info["desc"])
            sort_col.scroll_into_view_if_needed()
            for _ in range(2):
                if desc_val:
                    # If a descending is found, stop clicking
                    if sort_col.locator("svg.sort-arrow-down").count() > 0:
                        break
                else:
                    # If a ascending is found, stop clicking
                    if sort_col.locator("svg.sort-arrow-up").count() > 0:
                        break
                click_loc(sort_col, shift=shift)

    # TODO-karan-test: Add support for a list of columns ? If so, all other columns should be reset
    def set_filter(
        self,
        # TODO-barret support array of filters
        filter: ColumnFilter | list[ColumnFilter] | None,
        *,
        timeout: Timeout = None,
    ):
        """
        Set or reset filters for columns in a table or grid component.
        This method allows setting string filters, numeric range filters, or clearing all filters.

        Parameters
        ----------
        filter
            The filter to apply. Can be one of the following:
                * `None`: Resets all filters.
                * `ColumnFilterStr`: A dictionary specifying a string filter with 'col' and 'value' keys.
                * `ColumnFilterNumber`: A dictionary specifying a numeric range filter with 'col' and 'value' keys.
        timeout
            The maximum time to wait for the action to complete. Defaults to `None`.
        """
        # reset all filters
        all_input_locs = self.loc_column_filter.locator("> input, > div > input")
        for i in range(all_input_locs.count()):
            input_el = all_input_locs.nth(i)
            input_el.fill("", timeout=timeout)

        if filter is None:
            return

        if isinstance(filter, dict):
            filter = [filter]

        if not isinstance(filter, list):
            raise ValueError(
                "Invalid filter value. Must be a ColumnFilter, list[ColumnFilter], or None."
            )

        for filterInfo in filter:
            if "col" not in filterInfo:
                raise ValueError("Column index (`col`) is required for filtering.")

            if "value" not in filterInfo:
                raise ValueError("Filter value (`value`) is required for filtering.")

            filterColumn = self.loc_column_filter.nth(filterInfo["col"])

            if isinstance(filterInfo["value"], str):
                filterColumn.locator("> input").fill(filterInfo["value"])
            elif isinstance(filterInfo["value"], (tuple, list)):
                header_inputs = filterColumn.locator("> div > input")
                if filterInfo["value"][0] is not None:
                    header_inputs.nth(0).fill(
                        str(filterInfo["value"][0]),
                        timeout=timeout,
                    )
                if filterInfo["value"][1] is not None:
                    header_inputs.nth(1).fill(
                        str(filterInfo["value"][1]),
                        timeout=timeout,
                    )
            else:
                raise ValueError(
                    "Invalid filter value. Must be a string or a tuple/list of two numbers."
                )

    def set_cell(
        self,
        text: str,
        *,
        row: int,
        col: int,
        finish_key: (
            Literal["Enter", "Shift+Enter", "Tab", "Shift+Tab", "Escape"] | None
        ) = None,
        timeout: Timeout = None,
    ) -> None:
        """
        Saves the value of the cell in the data frame.

        Parameters
        ----------
        text
            The key to save the value of the cell.
        row
            The row number of the cell.
        col
            The column number of the cell.
        finish_key
            The key to save the value of the cell. If `None` (the default), no key will
            be pressed and instead the page body will be clicked.
        timeout
            The maximum time to wait for the action to complete. Defaults to `None`.
        """
        self._edit_cell_no_save(text, row=row, col=col, timeout=timeout)
        if finish_key is None:
            self.page.locator("body").click()
        else:
            self.cell_locator(row=row, col=col).locator("> textarea").press(finish_key)

    def expect_cell_title(
        self,
        value: str,
        *,
        row: int,
        col: int,
        timeout: Timeout = None,
    ) -> None:
        """
        Expects the validation message of the cell in the data frame, which will be in
        the `title` attribute of the element.

        Parameters
        ----------
        value
            The expected validation message of the cell.
        row
            The row number of the cell.
        col
            The column number of the cell.
        timeout
            The maximum time to wait for the expectation to pass. Defaults to `None`.
        """
        playwright_expect(self.cell_locator(row=row, col=col)).to_have_attribute(
            name="title", value=value, timeout=timeout
        )
