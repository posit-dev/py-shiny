from conftest import ShinyAppProc, x_create_doc_example_fixture
from controls import OutputTextVerbatim, Sidebar
from playwright.sync_api import Page

app = x_create_doc_example_fixture("sidebar")


def test_autoresize(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    left_sidebar = Sidebar(page, "sidebar_left")
    output_txt_left = OutputTextVerbatim(page, "state_left")
    left_sidebar.expect_title("Left sidebar content")
    output_txt_left.expect_value("input.sidebar_left(): True")
    left_sidebar.expect_handle(True)
    left_sidebar.expect_open(True)
    left_sidebar.loc_handle.click()
    left_sidebar.expect_open(False)
    output_txt_left.expect_value("input.sidebar_left(): False")

    right_sidebar = Sidebar(page, "sidebar_right")
    output_txt_right = OutputTextVerbatim(page, "state_right")
    right_sidebar.expect_title("Right sidebar content")
    output_txt_right.expect_value("input.sidebar_right(): True")
    right_sidebar.expect_handle(True)
    right_sidebar.expect_open(True)
    right_sidebar.loc_handle.click()
    right_sidebar.expect_open(False)
    output_txt_right.expect_value("input.sidebar_right(): False")

    closed_sidebar = Sidebar(page, "sidebar_closed")
    output_txt_closed = OutputTextVerbatim(page, "state_closed")
    output_txt_closed.expect_value("input.sidebar_closed(): False")
    closed_sidebar.expect_handle(True)
    closed_sidebar.expect_open(False)
    closed_sidebar.loc_handle.click()
    closed_sidebar.expect_title("Closed sidebar content")
    closed_sidebar.expect_open(True)
    output_txt_closed.expect_value("input.sidebar_closed(): True")

    always_sidebar = Sidebar(page, "sidebar_always")
    output_txt_always = OutputTextVerbatim(page, "state_always")
    always_sidebar.expect_title("Always sidebar content")
    output_txt_always.expect_value("input.sidebar_always(): False")
    always_sidebar.expect_handle(False)
