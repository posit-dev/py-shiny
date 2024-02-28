from __future__ import annotations

from typing import TypeVar

from conftest import ShinyAppProc, create_doc_example_core_fixture
from playwright.sync_api import Page

T = TypeVar("T")

app = create_doc_example_core_fixture("layout_columns")


def not_null(x: T | None) -> T:
    assert x is not None
    return x


def test_layout_columns(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    col1 = page.locator("#loss_over_time")
    col2 = page.locator("#accuracy_over_time")
    col3 = page.locator("#feature_importance")

    width1, width2, width3 = [
        not_null(x.bounding_box()).get("width") for x in [col1, col2, col3]
    ]

    assert width1 > 400
    assert width1 < width2
    assert width1 + width2 < width3
