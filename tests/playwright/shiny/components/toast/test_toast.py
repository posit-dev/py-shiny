from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_toast_basic(page: Page, local_app: ShinyAppProc) -> None:
    """Test basic toast display and visibility"""
    page.goto(local_app.url)

    # Show basic toast
    page.locator("#show_basic").click()

    # Verify toast is visible
    toast = controller.Toast(page, "basic-toast")
    toast.expect_visible()
    toast.expect_body("This is a basic toast notification")

    # Wait for auto-hide (default is 5 seconds, give it a bit more)
    toast.expect_hidden(timeout=10000)


def test_toast_types(page: Page, local_app: ShinyAppProc) -> None:
    """Test different toast types (success, warning, error)"""
    page.goto(local_app.url)

    # Test success toast
    page.locator("#show_success").click()
    success_toast = controller.Toast(page, "success-toast")
    success_toast.expect_visible()
    success_toast.expect_body("Operation completed successfully!")
    success_toast.expect_type("success")
    success_toast.expect_header("Success")

    # Test warning toast
    page.locator("#show_warning").click()
    warning_toast = controller.Toast(page, "warning-toast")
    warning_toast.expect_visible()
    warning_toast.expect_body("Please review the warnings.")
    warning_toast.expect_type("warning")
    warning_toast.expect_header("Warning")

    # Test error toast (error is aliased to danger)
    page.locator("#show_error").click()
    error_toast = controller.Toast(page, "error-toast")
    error_toast.expect_visible()
    error_toast.expect_body("An error occurred.")
    error_toast.expect_type("danger")
    error_toast.expect_header("Error")


def test_toast_header(page: Page, local_app: ShinyAppProc) -> None:
    """Test toast with structured header"""
    page.goto(local_app.url)

    page.locator("#show_with_header").click()
    toast = controller.Toast(page, "header-toast")
    toast.expect_visible()
    toast.expect_body("This toast has a structured header.")
    # The header should contain the text "Update Available"
    expect(toast.loc_header).to_contain_text("Update Available")


def test_toast_positions(page: Page, local_app: ShinyAppProc) -> None:
    """Test toast positioning"""
    page.goto(local_app.url)

    # Test top-left position
    page.locator("#show_top_left").click()
    top_left_toast = controller.Toast(page, "top-left-toast")
    top_left_toast.expect_visible()
    top_left_toast.expect_position("top-left")

    # Test bottom-right position
    page.locator("#show_bottom_right").click()
    bottom_right_toast = controller.Toast(page, "bottom-right-toast")
    bottom_right_toast.expect_visible()
    bottom_right_toast.expect_position("bottom-right")


def test_toast_persistent(page: Page, local_app: ShinyAppProc) -> None:
    """Test persistent toast (no auto-hide)"""
    page.goto(local_app.url)

    page.locator("#show_persistent").click()
    toast = controller.Toast(page, "persistent-toast")
    toast.expect_visible()
    toast.expect_autohide(False)

    # Wait a bit - toast should still be visible
    page.wait_for_timeout(3000)
    toast.expect_visible()


def test_toast_hide(page: Page, local_app: ShinyAppProc) -> None:
    """Test programmatic hide_toast()"""
    page.goto(local_app.url)

    # Show a persistent toast
    page.locator("#show_persistent").click()
    toast = controller.Toast(page, "persistent-toast")
    toast.expect_visible()

    # Hide the toast programmatically
    page.locator("#hide_toast_btn").click()
    toast.expect_hidden()


def test_toast_multiple(page: Page, local_app: ShinyAppProc) -> None:
    """Test multiple toasts can be shown simultaneously"""
    page.goto(local_app.url)

    # Show multiple toasts
    page.locator("#show_success").click()
    page.locator("#show_warning").click()

    # Both should be visible
    success_toast = controller.Toast(page, "success-toast")
    warning_toast = controller.Toast(page, "warning-toast")

    success_toast.expect_visible()
    warning_toast.expect_visible()
