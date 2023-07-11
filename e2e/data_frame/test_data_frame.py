# pyright: reportUnknownMemberType=false


import re
import time
from typing import Any, Callable

import pytest
from conftest import ShinyAppProc, create_example_fixture, expect_to_change
from controls import InputSelectize, InputSwitch
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

    return do


@pytest.mark.flaky
def test_grid_mode(
    page: Page, data_frame_app: ShinyAppProc, grid: Locator, grid_container: Locator
):
    page.goto(data_frame_app.url)

    # Ensure the output was found by Shiny
    expect(grid).to_have_class(re.compile(r"\bshiny-bound-output\b"))

    # Expect the data frame to be in grid mode by default
    expect(grid_container).not_to_have_class(re.compile(r"\bshiny-data-grid-table\b"))
    expect(grid_container).to_have_class(re.compile(r"\bshiny-data-grid-grid\b"))


@pytest.mark.flaky
def test_summary_navigation(
    page: Page, data_frame_app: ShinyAppProc, grid_container: Locator, summary: Locator
):
    page.goto(data_frame_app.url)

    # Check that summary responds to navigation
    expect(summary).to_have_text("Viewing rows 1 through 10 of 20")
    # Put focus in the table and hit End keystroke
    grid_container.locator("tbody tr:first-child td:first-child").click()
    with expect_to_change(lambda: summary.inner_text()):
        page.keyboard.press("End")
    # Ensure that summary updated
    expect(summary).to_have_text("Viewing rows 11 through 20 of 20")


@pytest.mark.flaky
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


@pytest.mark.flaky
def test_table_switch(
    page: Page,
    data_frame_app: ShinyAppProc,
    grid: Locator,
    grid_container: Locator,
    summary: Locator,
    scroll_to_end: Callable[[], None],
):
    page.goto(data_frame_app.url)
    select_dataset = InputSelectize(page, "dataset")

    scroll_to_end()

    # Switch to table
    InputSwitch(page, "gridstyle").toggle()
    expect(grid_container).not_to_have_class(re.compile(r"\bshiny-data-grid-grid\b"))
    expect(grid_container).to_have_class(re.compile(r"\bshiny-data-grid-table\b"))

    # Switching modes resets scroll
    expect(summary).to_have_text("Viewing rows 1 through 10 of 20")

    scroll_to_end()
    expect(summary).to_have_text("Viewing rows 11 through 20 of 20")

    # Switch datasets to much longer one
    select_dataset.set("diamonds")
    expect(summary).to_have_text("Viewing rows 1 through 10 of 53940")


@pytest.mark.flaky
def test_sort(
    page: Page,
    data_frame_app: ShinyAppProc,
    grid_container: Locator,
):
    page.goto(data_frame_app.url)
    select_dataset = InputSelectize(page, "dataset")
    select_dataset.set("diamonds")

    # Test sorting
    header_clarity = grid_container.locator("tr:first-child th:nth-child(4)")
    first_cell_clarity = grid_container.locator("tr:first-child td:nth-child(4)")
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


@pytest.mark.flaky
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


@pytest.mark.flaky
def test_single_selection(
    page: Page, data_frame_app: ShinyAppProc, grid_container: Locator, snapshot: Any
):
    page.goto(data_frame_app.url)
    InputSelectize(page, "selection_mode").set("single")
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


def retry_with_timeout(timeout: float = 30):
    def decorator(func: Callable[[], None]) -> None:
        def exec() -> None:
            start = time.time()
            while True:
                try:
                    return func()
                except AssertionError as e:
                    if time.time() - start > timeout:
                        raise e
                    time.sleep(0.1)

        exec()

    return decorator
