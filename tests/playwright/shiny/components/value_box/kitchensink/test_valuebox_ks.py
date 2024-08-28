from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.playwright.expect import expect_to_have_class
from shiny.run import ShinyAppProc


def get_value_box_bg_color(value_box: controller.ValueBox) -> str:
    value_box_bg_color = value_box.loc_container.evaluate(
        "el => window.getComputedStyle(el).getPropertyValue('background-color');"
    )
    return value_box_bg_color


def get_value_box_fg_color(value_box: controller.ValueBox) -> str:
    value_box_fg_color = value_box.loc_container.evaluate(
        "el => window.getComputedStyle(el).getPropertyValue('color');"
    )
    return value_box_fg_color


def get_title_tag_name(value_box: controller.ValueBox) -> str:
    title_tag_name = (
        value_box.loc_title.locator("*")
        .nth(0)
        .evaluate("el => el.tagName.toLowerCase()")
    )
    return title_tag_name


def get_value_tag_name(value_box: controller.ValueBox) -> str:
    value_tag_name = (
        value_box.loc.locator("*").nth(0).evaluate("el => el.tagName.toLowerCase()")
    )
    return value_tag_name


"""
For each value box we want to test
Layout and Positioning(e.g., showcase-top-right, showcase-left-center, showcase-bottom).
Title and Value Elements: The tests assert the tag names used for the title and value elements within each ValueBox (e.g., <span>, <p>, <h1>, <h3>, <h5>).
Fullscreen Availability and State: The tests check whether the fullscreen feature is available for a particular ValueBox and verify its initial state (fullscreen or not). For ValueBoxes with fullscreen support, the tests open and close the fullscreen mode and assert the expected behavior.
Background and Foreground Colors: The tests assert the background and foreground (text) colors applied to the ValueBox components.
Height: In some cases, the tests expect a specific height value for the ValueBox.
Content: The tests verify the expected title and value text displayed within each ValueBox. Additionally, for ValueBoxes with fullscreen support, the tests check the content displayed in fullscreen mode.
"""


def test_valuebox(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    value_box1 = controller.ValueBox(page, "valuebox1")
    value_box1.expect_height(None)
    # verify showcase layout uses 'showcase_top_right()'
    expect_to_have_class(value_box1.loc_container, "showcase-top-right")
    assert get_title_tag_name(value_box1) == "span"
    value_box1.expect_title("Red Color theme w/ Fullscreen")
    value_box1.expect_value("Showcase top right")
    assert get_value_tag_name(value_box1) == "h1"
    assert get_value_box_bg_color(value_box1) == "rgb(193, 0, 0)"
    assert get_value_box_fg_color(value_box1) == "rgb(255, 255, 255)"
    value_box1.expect_full_screen_available(True)
    value_box1.expect_full_screen(False)
    value_box1.set_full_screen(True)
    value_box1.expect_full_screen(True)
    value_box1.expect_body(["Inside the fullscreen"])
    value_box1.set_full_screen(False)
    value_box1.expect_full_screen(False)

    value_box2 = controller.ValueBox(page, "valuebox2")
    value_box2.expect_height(None)
    # verify showcase layout uses 'showcase_left_center()'
    expect_to_have_class(value_box2.loc_container, "showcase-left-center")
    assert get_title_tag_name(value_box2) == "p"
    value_box2.expect_title("Primary theme w/o Fullscreen")
    value_box2.expect_value("Showcase left center")
    assert get_value_tag_name(value_box2) == "h5"
    assert get_value_box_bg_color(value_box2) == "rgb(0, 123, 194)"
    value_box2.expect_full_screen_available(False)

    value_box3 = controller.ValueBox(page, "valuebox3")
    value_box3.expect_height(None)
    # verify showcase layout uses 'showcase_bottom()'
    expect_to_have_class(value_box3.loc_container, "showcase-bottom")
    assert get_title_tag_name(value_box3) == "span"
    value_box3.expect_title("No theme w/ Fullscreen")
    value_box3.expect_value("Showcase bottom")
    assert get_value_tag_name(value_box3) == "h3"
    value_box3.expect_full_screen_available(True)
    assert get_value_box_bg_color(value_box3) == "rgb(255, 255, 255)"

    value_box4 = controller.ValueBox(page, "valuebox4")
    value_box4.expect_height(None)
    value_box4.expect_title("No showcase - w/o Fullscreen (default)")
    value_box4.expect_value("No theme - only defaults")
    assert get_title_tag_name(value_box4) == "p"
    assert get_title_tag_name(value_box4) == "p"
    value_box4.expect_full_screen_available(False)
    assert get_value_box_bg_color(value_box4) == "rgb(255, 255, 255)"

    value_box5 = controller.ValueBox(page, "valuebox5")
    value_box5.expect_height("500px")
    assert get_title_tag_name(value_box5) == "p"
    value_box5.expect_title("No showcase w/ showcase layout")
    value_box5.expect_value("Red text - fill is False")
    assert get_value_tag_name(value_box5) == "p"
    value_box5.expect_full_screen_available(False)
    assert get_value_box_bg_color(value_box5) == "rgb(255, 255, 255)"
    assert get_value_box_fg_color(value_box5) == "rgb(193, 0, 0)"
