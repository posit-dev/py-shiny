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

    right_sidebar = Sidebar(page, "sidebar_right")
    output_txt_right = OutputTextVerbatim(page, "state_right")
    output_txt_right.expect_value("input.sidebar_right(): True")
    right_sidebar.expect_toggle_button(True)
    right_sidebar.expect_toggle_to_be_true()
    right_sidebar.loc_toggle.click()
    right_sidebar.expect_toggle_to_be_false()
    output_txt_right.expect_value("input.sidebar_right(): False")

    closed_sidebar = Sidebar(page, "sidebar_closed")
    output_txt_closed = OutputTextVerbatim(page, "state_closed")
    output_txt_closed.expect_value("input.sidebar_closed(): False")
    closed_sidebar.expect_toggle_button(True)
    closed_sidebar.expect_toggle_to_be_false()
    closed_sidebar.loc_toggle.click()
    closed_sidebar.expect_toggle_to_be_true()
    output_txt_closed.expect_value("input.sidebar_closed(): True")

    always_sidebar = Sidebar(page, "sidebar_always")
    output_txt_always = OutputTextVerbatim(page, "state_always")
    output_txt_always.expect_value("input.sidebar_always(): False")
    always_sidebar.expect_toggle_button(False)


