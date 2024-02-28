# pyright: reportUnknownMemberType=false

import re
import time
from typing import Any, Callable

import pytest
from conftest import ShinyAppProc, create_example_fixture, expect_to_change
from controls import InputSelect, InputSwitch
from examples.example_apps import reruns, reruns_delay
from playwright.sync_api import Locator, Page, expect

data_frame_app = create_example_fixture("dataframe")


@pytest.fixture
def grid(page: Page) -> Locator:
    return page.locator("#grid")


@pytest.fixture
def grid_container(page: Page, grid: Locator) -> Locator:
    return grid.locator("> div > div.shiny-data-grid")


@pytest.fixture
def summary(page: Page, grid: Locator) -> Locator:
    return grid.locator("div.shiny-data-grid-summary")


@pytest.fixture
def scroll_to_end(page: Page, grid_container: Locator) -> Callable[[], None]:
    def do():
        grid_container.locator("tbody tr:first-child td:first-child").click()
        page.keyboard.press("End")

        # Starting some time around January 19, 2024, Firefox doesn't scroll to the end
        # of the table when the End button is pressed. Repros on real Firefox 121.0.1
        # (64-bit) on macOS. This is a workaround to get the test suite to pass.
        if page.context.browser and page.context.browser.browser_type.name == "firefox":
            time.sleep(0.1)
            page.keyboard.press("End")
            time.sleep(0.1)
            page.keyboard.press("End")

    return do


@pytest.mark.flaky(reruns=reruns, delay=reruns_delay)
def test_grid_mode(
    page: Page, data_frame_app: ShinyAppProc, grid: Locator, grid_container: Locator
):
    page.goto(data_frame_app.url)

    # Ensure the output was found by Shiny
    expect(grid).to_have_class(re.compile(r"\bshiny-bound-output\b"))

    # Expect the data frame to be in grid mode by default
    expect(grid_container).not_to_have_class(re.compile(r"\bshiny-data-grid-table\b"))
    expect(grid_container).to_have_class(re.compile(r"\bshiny-data-grid-grid\b"))


@pytest.mark.flaky(reruns=reruns, delay=reruns_delay)
def test_summary_navigation(
    page: Page,
    data_frame_app: ShinyAppProc,
    grid_container: Locator,
    summary: Locator,
    scroll_to_end: Callable[[], None],
):
    page.goto(data_frame_app.url)

    # Check that summary responds to navigation
    expect(summary).to_have_text(re.compile("^Viewing rows 1 through \\d+ of 20$"))
    # Put focus in the table and hit End keystroke
    grid_container.locator("tbody tr:first-child td:first-child").click()
    with expect_to_change(lambda: summary.inner_text()):
        scroll_to_end()
    # Ensure that summary updated
    expect(summary).to_have_text(re.compile("^Viewing rows \\d+ through 20 of 20$"))


@pytest.mark.flaky(reruns=reruns, delay=reruns_delay)
def test_full_width(page: Page, data_frame_app: ShinyAppProc, grid_container: Locator):
    page.goto(data_frame_app.url)

    def get_width() -> float:
        rect = grid_container.bounding_box()
        return rect.get("width", 0) if rect else 0

    width1 = get_width()
    # Switch to narrow mode
    with expect_to_change(get_width):
        InputSwitch(page, "fullwidth").toggle()
    width2 = get_width()

    assert width2 < width1

    # Switch back to full width
    InputSwitch(page, "fullwidth").toggle()


@pytest.mark.flaky(reruns=reruns, delay=reruns_delay)
def test_table_switch(
    page: Page,
    data_frame_app: ShinyAppProc,
    grid: Locator,
    grid_container: Locator,
    summary: Locator,
    scroll_to_end: Callable[[], None],
):
    page.goto(data_frame_app.url)
    select_dataset = InputSelect(page, "dataset")

    scroll_to_end()

    # Switch to table
    InputSwitch(page, "gridstyle").toggle()
    expect(grid_container).not_to_have_class(re.compile(r"\bshiny-data-grid-grid\b"))
    expect(grid_container).to_have_class(re.compile(r"\bshiny-data-grid-table\b"))

    # Switching modes resets scroll
    expect(summary).to_have_text(re.compile("^Viewing rows 1 through \\d+ of 20$"))

    scroll_to_end()
    expect(summary).to_have_text(re.compile("^Viewing rows \\d+ through 20 of 20$"))

    # Switch datasets to much longer one
    select_dataset.set("diamonds")
    select_dataset.expect.to_have_value("diamonds")
    expect(summary).to_have_text(
        re.compile("^Viewing rows 1 through \\d+ of 53940$"), timeout=10000
    )


@pytest.mark.flaky(reruns=reruns, delay=reruns_delay)
def test_sort(
    page: Page,
    data_frame_app: ShinyAppProc,
    grid_container: Locator,
):
    page.goto(data_frame_app.url)
    select_dataset = InputSelect(page, "dataset")
    select_dataset.set("diamonds")
    select_dataset.expect.to_have_value("diamonds")

    # Table cell locators
    header_clarity = grid_container.locator("tr:first-child th:nth-child(4)")
    first_cell_clarity = grid_container.locator("tr:first-child td:nth-child(4)")

    # Test that the table contents have updated
    # This may timeout unless a larger timeout is given
    expect(header_clarity).not_to_have_text(
        "num2",
        timeout=15 * 1000,  # Larger timeout for CI
    )
    expect(first_cell_clarity).not_to_have_text("4")

    # Test sorting
    expect(first_cell_clarity).to_have_text("SI2")
    header_clarity.click()
    expect(first_cell_clarity).to_have_text("I1")
    header_clarity.click()
    expect(first_cell_clarity).to_have_text("VVS2")

    # Test multi-sorting
    depth_clarity = grid_container.locator("tr:first-child th:nth-child(5)")
    first_cell_depth = grid_container.locator("tr:first-child td:nth-child(5)")
    depth_clarity.click(modifiers=["Shift"])
    expect(first_cell_depth).to_have_text("67.6")


@pytest.mark.flaky(reruns=reruns, delay=reruns_delay)
def test_multi_selection(
    page: Page, data_frame_app: ShinyAppProc, grid_container: Locator, snapshot: Any
):
    page.goto(data_frame_app.url)
    first_cell = grid_container.locator("tbody tr:first-child td:first-child")

    def detail_text():
        return page.locator("#detail").inner_text()

    expect(first_cell).to_have_text("1")
    with expect_to_change(detail_text):
        first_cell.click()

    assert detail_text() == snapshot

    kb = page.keyboard
    with expect_to_change(lambda: grid_container.locator(":focus").inner_text()):
        kb.press("ArrowDown")
    with expect_to_change(lambda: grid_container.locator(":focus").inner_text()):
        kb.press("ArrowDown")
    with expect_to_change(detail_text):
        kb.press("Space")
    with expect_to_change(lambda: grid_container.locator(":focus").inner_text()):
        kb.press("ArrowDown")
    with expect_to_change(detail_text):
        kb.press("Enter")
    assert detail_text() == snapshot


@pytest.mark.flaky(reruns=reruns, delay=reruns_delay)
def test_single_selection(
    page: Page, data_frame_app: ShinyAppProc, grid_container: Locator, snapshot: Any
):
    page.goto(data_frame_app.url)
    InputSelect(page, "selection_mode").set("single")
    first_cell = grid_container.locator("tbody tr:first-child td:first-child")

    def detail_text():
        return page.locator("#detail").inner_text()

    expect(first_cell).to_have_text("1")
    with expect_to_change(detail_text):
        first_cell.click()

    assert detail_text() == snapshot

    kb = page.keyboard
    with expect_to_change(detail_text):
        kb.press("ArrowDown")
    with expect_to_change(detail_text):
        kb.press("ArrowDown")
    with expect_to_change(detail_text):
        kb.press("Space")
    with expect_to_change(lambda: grid_container.locator(":focus").inner_text()):
        kb.press("ArrowDown")
    with expect_to_change(detail_text):
        kb.press("Enter")
    assert detail_text() == snapshot


def test_filter_grid(
    page: Page,
    data_frame_app: ShinyAppProc,
    grid: Locator,
    summary: Locator,
    snapshot: Any,
):
    page.goto(data_frame_app.url)
    _filter_test_impl(page, data_frame_app, grid, summary, snapshot)


def test_filter_table(
    page: Page,
    data_frame_app: ShinyAppProc,
    grid: Locator,
    grid_container: Locator,
    summary: Locator,
    snapshot: Any,
):
    page.goto(data_frame_app.url)

    InputSwitch(page, "gridstyle").toggle()
    expect(grid_container).not_to_have_class(re.compile(r"\bshiny-data-grid-grid\b"))
    expect(grid_container).to_have_class(re.compile(r"\bshiny-data-grid-table\b"))

    _filter_test_impl(page, data_frame_app, grid, summary, snapshot)


def _filter_test_impl(
    page: Page,
    data_frame_app: ShinyAppProc,
    grid: Locator,
    summary: Locator,
    snapshot: Any,
):
    filters = grid.locator("tr.filters")

    filter_subidir_min = filters.locator("> th:nth-child(1) > div > input:nth-child(1)")
    filter_subidir_max = filters.locator("> th:nth-child(1) > div > input:nth-child(2)")
    filter_attnr = filters.locator("> th:nth-child(2) > input")
    filter_num1_min = filters.locator("> th:nth-child(3) > div > input:nth-child(1)")
    filter_num1_max = filters.locator("> th:nth-child(3) > div > input:nth-child(2)")

    expect(filter_subidir_min).to_be_visible()
    expect(filter_subidir_max).to_be_visible()
    expect(filter_attnr).to_be_visible()
    expect(filter_num1_min).to_be_visible()
    expect(filter_num1_max).to_be_visible()

    expect(summary).to_be_visible()
    expect(summary).to_have_text(re.compile(" of 20$"))

    # Placeholder text only appears when filter is focused
    expect(page.get_by_placeholder("Min (1)", exact=True)).not_to_be_attached()
    expect(page.get_by_placeholder("Max (20)", exact=True)).not_to_be_attached()
    filter_subidir_min.focus()
    expect(page.get_by_placeholder("Min (1)", exact=True)).to_be_attached()
    expect(page.get_by_placeholder("Max (20)", exact=True)).to_be_attached()
    filter_subidir_min.blur()
    expect(page.get_by_placeholder("Min (1)", exact=True)).not_to_be_attached()
    expect(page.get_by_placeholder("Max (20)", exact=True)).not_to_be_attached()

    # Make sure that filtering input results in correct number of rows

    # Test only min
    filter_subidir_min.fill("5")
    expect(summary).to_have_text(re.compile(" of 16$"))
    # Test min and max
    filter_subidir_max.fill("14")
    expect(summary).to_have_text(re.compile(" of 10$"))

    # When filtering results in all rows being shown, the summary should not be visible
    filter_subidir_max.fill("11")
    expect(summary).not_to_be_attached()

    # Test only max
    filter_subidir_min.fill("")
    expect(summary).to_have_text(re.compile(" of 11"))

    filter_subidir_min.clear()
    filter_subidir_max.clear()

    # Try substring search
    filter_attnr.fill("oc")
    expect(summary).to_have_text(re.compile(" of 10"))
    filter_num1_min.focus()
    # Ensure other columns' filter placeholders show faceted results
    expect(page.get_by_placeholder("Min (5)", exact=True)).to_be_attached()
    expect(page.get_by_placeholder("Max (8)", exact=True)).to_be_attached()

    # Filter down to zero matching rows
    filter_attnr.fill("q")
    # Summary should be gone
    expect(summary).not_to_be_attached()
    filter_num1_min.focus()
    # Placeholders should not have values
    expect(page.get_by_placeholder("Min", exact=True)).to_be_attached()
    expect(page.get_by_placeholder("Max", exact=True)).to_be_attached()

    filter_attnr.clear()

    # Apply multiple filters, make sure we get the correct results
    filter_subidir_max.fill("8")
    # We had a bug before where typing in a decimal point would cause
    # the cursor to jump to the front. Make sure that doesn't happen.
    filter_num1_min.focus()
    page.keyboard.press("3")
    time.sleep(0.2)
    page.keyboard.press(".")
    time.sleep(0.2)
    page.keyboard.press("9")
    expect(grid.locator("tbody tr")).to_have_count(5)

    # Ensure changing dataset resets filters
    select_dataset = InputSelect(page, "dataset")
    select_dataset.set("attention")
    select_dataset.expect.to_have_value("attention")
    expect(page.get_by_text("Unnamed: 0")).to_be_attached()
    select_dataset.set("anagrams")
    select_dataset.expect.to_have_value("anagrams")
    expect(summary).to_have_text(re.compile(" of 20"))


def test_filter_disable(page: Page, data_frame_app: ShinyAppProc):
    page.goto(data_frame_app.url)

    expect(page.locator("tr.filters")).to_be_attached()
    InputSwitch(page, "filters").toggle()
    expect(page.locator("tr.filters")).not_to_be_attached()
