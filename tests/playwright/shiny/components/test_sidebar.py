from conftest import ShinyAppProc, create_doc_example_fixture
from controls import OutputTextVerbatim, Sidebar
from playwright.sync_api import Page

app = create_doc_example_fixture("sidebar")


def test_sidebar_position_and_open(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    left_sidebar = Sidebar(page, "sidebar_left")
    output_txt_left = OutputTextVerbatim(page, "state_left")
    left_sidebar.set(True)
    output_txt_left.expect_value("input.sidebar_left(): True")
    left_sidebar.expect_open(True)
    left_sidebar.set(False)
    output_txt_left.expect_value("input.sidebar_left(): False")
    left_sidebar.expect_text("Left sidebar content")
    left_sidebar.expect_handle(True)
    left_sidebar.expect_open(False)
    left_sidebar.loc_handle.click()
    left_sidebar.expect_open(False)
    output_txt_left.expect_value("input.sidebar_left(): False")

    right_sidebar = Sidebar(page, "sidebar_right")
    output_txt_right = OutputTextVerbatim(page, "state_right")
    right_sidebar.expect_text("Right sidebar content")
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
    closed_sidebar.expect_text("Closed sidebar content")
    closed_sidebar.expect_open(True)
    output_txt_closed.expect_value("input.sidebar_closed(): True")

    always_sidebar = Sidebar(page, "sidebar_always")
    output_txt_always = OutputTextVerbatim(page, "state_always")
    always_sidebar.expect_text("Always sidebar content")
    output_txt_always.expect_value("input.sidebar_always(): True")
    always_sidebar.expect_handle(False)
