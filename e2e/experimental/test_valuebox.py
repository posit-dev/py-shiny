from conftest import ShinyAppProc, x_create_doc_example_fixture
from controls import ValueBox
from playwright.sync_api import Page

app = x_create_doc_example_fixture("value_box")


def test_valuebox(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    value_box = ValueBox(page, "valuecard1")
    value_box.expect_height(None)
    value_box.expect_title_to_contain_text("KPI Title")
    value_box.expect_body_to_contain_text("$1 Billion Dollars")
    value_box.expect_footer_to_contain_text("30% VS PREVIOUS 30 DAYS")
    value_box.expect_showcase_max_height("100px")
    value_box.expect_showcase_max_height_full_screen("67%")
