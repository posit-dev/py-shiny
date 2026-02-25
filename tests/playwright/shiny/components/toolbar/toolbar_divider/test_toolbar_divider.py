import pytest
from conftest import create_app_fixture
from playwright.sync_api import Page, expect

from shiny.run import ShinyAppProc

app = create_app_fixture("./app.py")


@pytest.mark.flaky(reruns=3)
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


@pytest.mark.flaky(reruns=3)
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


@pytest.mark.flaky(reruns=3)
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


@pytest.mark.flaky(reruns=3)
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


@pytest.mark.flaky(reruns=3)
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


@pytest.mark.flaky(reruns=3)
def test_toolbar_multiple_dividers(page: Page, app: ShinyAppProc) -> None:
    """Test multiple dividers in a single toolbar."""
    page.goto(app.url)

    # Find Test 6 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(5)  # Sixth toolbar (Test 6)

    # Should have 3 dividers between 4 buttons
    dividers = toolbar.locator(".bslib-toolbar-divider")
    expect(dividers).to_have_count(3)


@pytest.mark.flaky(reruns=3)
def test_toolbar_divider_aria_hidden(page: Page, app: ShinyAppProc) -> None:
    """Test that dividers have aria-hidden attribute."""
    page.goto(app.url)

    divider = page.locator(".bslib-toolbar-divider").first
    expect(divider).to_have_attribute("aria-hidden", "true")


@pytest.mark.flaky(reruns=3)
def test_toolbar_spacer_basic(page: Page, app: ShinyAppProc) -> None:
    """Test basic toolbar_spacer functionality."""
    page.goto(app.url)

    # Find Test 7 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(6)  # Seventh toolbar (Test 7)

    spacer = toolbar.locator(".bslib-toolbar-spacer").first
    # Spacer exists in the DOM (but is not "visible" due to aria-hidden and empty content)
    expect(spacer).to_be_attached()

    # Spacer should have aria-hidden
    expect(spacer).to_have_attribute("aria-hidden", "true")


@pytest.mark.flaky(reruns=3)
def test_toolbar_spacer_layout(page: Page, app: ShinyAppProc) -> None:
    """Test that spacer creates proper layout spacing."""
    page.goto(app.url)

    # Find Test 7 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(6)  # Seventh toolbar (Test 7)

    left_btn = toolbar.locator("#btn_spacer_left")
    right_btn = toolbar.locator("#btn_spacer_right")
    spacer = toolbar.locator(".bslib-toolbar-spacer")

    # Buttons should be visible, spacer exists but is not "visible"
    expect(left_btn).to_be_visible()
    expect(spacer).to_be_attached()
    expect(right_btn).to_be_visible()

    # Get bounding boxes
    left_box = left_btn.bounding_box()
    right_box = right_btn.bounding_box()

    # Buttons should be far apart (spacer pushes them to opposite ends)
    assert left_box is not None
    assert right_box is not None
    # Right button should be significantly to the right of left button
    assert right_box["x"] > left_box["x"] + 100


@pytest.mark.flaky(reruns=3)
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

    # Verify spacer creates separation between left and right button groups
    left_btn2 = toolbar.locator("#btn_spacer_left2")  # Last button on left
    right_btn1 = toolbar.locator("#btn_spacer_right1")  # First button on right

    left_box = left_btn2.bounding_box()
    right_box = right_btn1.bounding_box()

    assert left_box is not None
    assert right_box is not None
    # Right button group should be significantly to the right of left button group
    assert right_box["x"] > left_box["x"] + left_box["width"] + 50


@pytest.mark.flaky(reruns=3)
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

    # Verify spacer creates separation between left and right groups
    left_btn4 = toolbar.locator("#btn_combo_left4")  # Last button before spacer
    right_btn1 = toolbar.locator("#btn_combo_right1")  # First button after spacer

    left_box = left_btn4.bounding_box()
    right_box = right_btn1.bounding_box()

    assert left_box is not None
    assert right_box is not None
    # Right button should be significantly to the right of left group
    assert right_box["x"] > left_box["x"] + left_box["width"] + 50


@pytest.mark.flaky(reruns=3)
def test_toolbar_multiple_spacers(page: Page, app: ShinyAppProc) -> None:
    """Test multiple spacers in a toolbar (edge case)."""
    page.goto(app.url)

    # Find Test 10 toolbar
    toolbars = page.locator(".bslib-toolbar")
    toolbar = toolbars.nth(9)  # Tenth toolbar (Test 10)

    # Should have 2 spacers
    spacers = toolbar.locator(".bslib-toolbar-spacer")
    expect(spacers).to_have_count(2)

    # Verify only the first spacer creates spacing (expected behavior)
    btn1 = toolbar.locator("#btn_edge1")
    btn2 = toolbar.locator("#btn_edge2")
    btn3 = toolbar.locator("#btn_edge3")

    box1 = btn1.bounding_box()
    box2 = btn2.bounding_box()
    box3 = btn3.bounding_box()

    assert box1 is not None
    assert box2 is not None
    assert box3 is not None

    # First spacer should create significant gap between btn1 and btn2
    assert box2["x"] > box1["x"] + box1["width"] + 50

    # Second spacer might not work as expected, but btn2 and btn3 should be close
    # (or far apart if second spacer also works - implementation dependent)


@pytest.mark.flaky(reruns=3)
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


@pytest.mark.flaky(reruns=3)
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

    # Verify spacer creates separation even with align="right"
    left_btn = toolbar.locator("#btn_align_left")
    right_btn = toolbar.locator("#btn_align_right")

    left_box = left_btn.bounding_box()
    right_box = right_btn.bounding_box()

    assert left_box is not None
    assert right_box is not None
    # Right button should be significantly to the right of left button
    assert right_box["x"] > left_box["x"] + left_box["width"] + 50
