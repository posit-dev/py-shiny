from conftest import ShinyAppProc, create_app_fixture
from playwright.sync_api import Page, expect

from shiny.run import ShinyAppProc

app = create_app_fixture("./app.py")


def test_toolbar_divider_exists(page: Page, app: ShinyAppProc) -> None:
    """Test that toolbar dividers are present in the DOM."""
    page.goto(app.url)

    # Check that dividers exist with the correct class
    dividers = page.locator(".bslib-toolbar-divider")
    expect(dividers).to_have_count(17)  # Total dividers across all test cases


def test_toolbar_divider_default(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar_divider() with default settings."""
    page.goto(app.url)

    # Find the first toolbar with divider
    toolbar = page.locator(".bslib-toolbar").first
    divider = toolbar.locator(".bslib-toolbar-divider").first

    # Divider should be present
    expect(divider).to_be_visible()

    # Check default styling is not explicitly set (uses CSS defaults)
    style = divider.get_attribute("style")
    # Default values shouldn't be in inline styles since they're CSS defaults
    assert style is None or style == ""


def test_toolbar_divider_custom_width(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar_divider with custom width."""
    page.goto(app.url)

    # Find Test 2 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(1)  # Second toolbar (Test 2)
    divider = toolbar.locator(".bslib-toolbar-divider").first

    # Check custom width is set
    style = divider.get_attribute("style")
    assert style is not None
    assert "--_divider-width: 5px" in style or "--_divider-width:5px" in style


def test_toolbar_divider_custom_gap(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar_divider with custom gap."""
    page.goto(app.url)

    # Find Test 3 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(2)  # Third toolbar (Test 3)
    divider = toolbar.locator(".bslib-toolbar-divider").first

    # Check custom gap is set
    style = divider.get_attribute("style")
    assert style is not None
    assert "--_divider-gap: 2rem" in style or "--_divider-gap:2rem" in style


def test_toolbar_divider_custom_width_and_gap(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar_divider with both custom width and gap."""
    page.goto(app.url)

    # Find Test 4 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(3)  # Fourth toolbar (Test 4)
    divider = toolbar.locator(".bslib-toolbar-divider").first

    # Check both custom properties are set
    style = divider.get_attribute("style")
    assert style is not None
    assert "--_divider-width: 3px" in style or "--_divider-width:3px" in style
    assert "--_divider-gap: 1.5rem" in style or "--_divider-gap:1.5rem" in style


def test_toolbar_divider_no_line(page: Page, app: ShinyAppProc) -> None:
    """Test toolbar_divider with width='0px' (spacing only, no line)."""
    page.goto(app.url)

    # Find Test 5 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(4)  # Fifth toolbar (Test 5)
    divider = toolbar.locator(".bslib-toolbar-divider").first

    # Check width is 0px
    style = divider.get_attribute("style")
    assert style is not None
    assert "--_divider-width: 0px" in style or "--_divider-width:0px" in style
    assert "--_divider-gap: 2rem" in style or "--_divider-gap:2rem" in style


def test_toolbar_multiple_dividers(page: Page, app: ShinyAppProc) -> None:
    """Test multiple dividers in a single toolbar."""
    page.goto(app.url)

    # Find Test 6 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(5)  # Sixth toolbar (Test 6)

    # Should have 3 dividers between 4 buttons
    dividers = toolbar.locator(".bslib-toolbar-divider")
    expect(dividers).to_have_count(3)


def test_toolbar_divider_aria_hidden(page: Page, app: ShinyAppProc) -> None:
    """Test that dividers have aria-hidden attribute."""
    page.goto(app.url)

    divider = page.locator(".bslib-toolbar-divider").first
    expect(divider).to_have_attribute("aria-hidden", "true")


def test_toolbar_spacer_exists(page: Page, app: ShinyAppProc) -> None:
    """Test that toolbar spacers are present in the DOM."""
    page.goto(app.url)

    # Check that spacers exist with the correct class
    spacers = page.locator(".bslib-toolbar-spacer")
    expect(spacers).to_have_count(5)  # Total spacers across test cases


def test_toolbar_spacer_basic(page: Page, app: ShinyAppProc) -> None:
    """Test basic toolbar_spacer functionality."""
    page.goto(app.url)

    # Find Test 7 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(6)  # Seventh toolbar (Test 7)

    spacer = toolbar.locator(".bslib-toolbar-spacer").first
    expect(spacer).to_be_visible()

    # Spacer should have aria-hidden
    expect(spacer).to_have_attribute("aria-hidden", "true")


def test_toolbar_spacer_layout(page: Page, app: ShinyAppProc) -> None:
    """Test that spacer creates proper layout spacing."""
    page.goto(app.url)

    # Find Test 7 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(6)  # Seventh toolbar (Test 7)

    left_btn = toolbar.locator("#btn_spacer_left")
    right_btn = toolbar.locator("#btn_spacer_right")
    spacer = toolbar.locator(".bslib-toolbar-spacer")

    # All elements should exist
    expect(left_btn).to_be_visible()
    expect(spacer).to_be_visible()
    expect(right_btn).to_be_visible()

    # Get bounding boxes
    left_box = left_btn.bounding_box()
    right_box = right_btn.bounding_box()

    # Buttons should be far apart (spacer pushes them to opposite ends)
    assert left_box is not None
    assert right_box is not None
    # Right button should be significantly to the right of left button
    assert right_box["x"] > left_box["x"] + 100


def test_toolbar_spacer_multiple_items(page: Page, app: ShinyAppProc) -> None:
    """Test spacer with multiple items on each side."""
    page.goto(app.url)

    # Find Test 8 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(7)  # Eighth toolbar (Test 8)

    # Should have 4 buttons and 1 spacer
    buttons = toolbar.locator(".bslib-toolbar-input-button")
    expect(buttons).to_have_count(4)

    spacer = toolbar.locator(".bslib-toolbar-spacer")
    expect(spacer).to_have_count(1)


def test_toolbar_divider_and_spacer_combined(page: Page, app: ShinyAppProc) -> None:
    """Test combining toolbar_divider and toolbar_spacer."""
    page.goto(app.url)

    # Find Test 9 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(8)  # Ninth toolbar (Test 9)

    # Should have both divider and spacer
    divider = toolbar.locator(".bslib-toolbar-divider")
    expect(divider).to_have_count(1)

    spacer = toolbar.locator(".bslib-toolbar-spacer")
    expect(spacer).to_have_count(1)

    # Should have 5 buttons
    buttons = toolbar.locator(".bslib-toolbar-input-button")
    expect(buttons).to_have_count(5)


def test_toolbar_multiple_spacers(page: Page, app: ShinyAppProc) -> None:
    """Test multiple spacers in a toolbar (edge case)."""
    page.goto(app.url)

    # Find Test 10 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(9)  # Tenth toolbar (Test 10)

    # Should have 2 spacers
    spacers = toolbar.locator(".bslib-toolbar-spacer")
    expect(spacers).to_have_count(2)


def test_toolbar_dividers_varying_properties(page: Page, app: ShinyAppProc) -> None:
    """Test multiple dividers with different custom properties."""
    page.goto(app.url)

    # Find Test 11 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(10)  # Eleventh toolbar (Test 11)

    dividers = toolbar.locator(".bslib-toolbar-divider")
    expect(dividers).to_have_count(3)

    # Check first divider (1px, 0.5rem)
    style1 = dividers.nth(0).get_attribute("style")
    assert style1 is not None
    assert "--_divider-width: 1px" in style1 or "--_divider-width:1px" in style1
    assert "--_divider-gap: 0.5rem" in style1 or "--_divider-gap:0.5rem" in style1

    # Check second divider (4px, 1rem)
    style2 = dividers.nth(1).get_attribute("style")
    assert style2 is not None
    assert "--_divider-width: 4px" in style2 or "--_divider-width:4px" in style2
    assert "--_divider-gap: 1rem" in style2 or "--_divider-gap:1rem" in style2

    # Check third divider (2px, 2rem)
    style3 = dividers.nth(2).get_attribute("style")
    assert style3 is not None
    assert "--_divider-width: 2px" in style3 or "--_divider-width:2px" in style3
    assert "--_divider-gap: 2rem" in style3 or "--_divider-gap:2rem" in style3


def test_toolbar_spacer_with_align_right(page: Page, app: ShinyAppProc) -> None:
    """Test spacer works with align='right' toolbar."""
    page.goto(app.url)

    # Find Test 12 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(11)  # Twelfth toolbar (Test 12)

    # Check toolbar has align="right"
    expect(toolbar).to_have_attribute("data-align", "right")

    # Should still have spacer
    spacer = toolbar.locator(".bslib-toolbar-spacer")
    expect(spacer).to_have_count(1)
