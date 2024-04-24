from conftest import ShinyAppProc
from controls import OutputTextVerbatim
from playwright.sync_api import Page

@pytest.mark.skip(reason="Flaky test. Fix before renabling")
def test_output_image_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    OutputTextVerbatim(page, "no_output").expect_value("DATA SUMMARY")
    OutputTextVerbatim(page, "no_parens").expect_value("DATA SUMMARY")
    OutputTextVerbatim(page, "to_upper").expect_value("DATA SUMMARY")
    OutputTextVerbatim(page, "to_lower").expect_value("data summary")
