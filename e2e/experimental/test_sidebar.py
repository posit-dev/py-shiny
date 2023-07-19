from conftest import ShinyAppProc, x_create_doc_example_fixture
from controls import OutputTextVerbatim, Sidebar
from playwright.sync_api import Page

app = x_create_doc_example_fixture("sidebar")


def test_autoresize(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    left_sidebar = Sidebar(page, "sidebar_left")
    output_txt_left = OutputTextVerbatim(page, "state_left")
    output_txt_left.expect_value("input.sidebar_left(): True")
    left_sidebar.expect_toggle_button(True)
    left_sidebar.expect_toggle_to_be_true()
    left_sidebar.loc_toggle.click()
    left_sidebar.expect_toggle_to_be_false()
    output_txt_left.expect_value("input.sidebar_left(): False")
