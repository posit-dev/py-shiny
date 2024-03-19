from conftest import ShinyAppProc
from controls import ValueBox, expect_to_have_class
from playwright.sync_api import Page


def get_value_box_bg_color(value_box: ValueBox) -> str:
    value_box_bg_color = value_box.loc_container.evaluate(
        "el => window.getComputedStyle(el).getPropertyValue('background-color');"
    )
    return value_box_bg_color

def get_value_box_fg_color(value_box: ValueBox) -> str:
    value_box_fg_color = value_box.loc_container.evaluate(
        "el => window.getComputedStyle(el).getPropertyValue('color');"
    )
    return value_box_fg_color

def get_title_tag_name(value_box: ValueBox) -> str:
    title_tag_name = (
        value_box.loc_title.locator("*")
        .nth(0)
        .evaluate("el => el.tagName.toLowerCase()")
    )
    return title_tag_name


def get_value_tag_name(value_box: ValueBox) -> str:
    value_tag_name = (
        value_box.loc.locator("*").nth(0).evaluate("el => el.tagName.toLowerCase()")
    )
    return value_tag_name


def test_valuebox(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    value_box1 = ValueBox(page, "valuebox1")
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
    value_box1.open_full_screen()
    value_box1.expect_full_screen(True)
    value_box1.expect_body(["Inside the fullscreen"])
    value_box1.close_full_screen()
    value_box1.expect_full_screen(False)

    value_box2 = ValueBox(page, "valuebox2")
    value_box2.expect_height(None)
    # verify showcase layout uses 'showcase_left_center()'
    expect_to_have_class(value_box2.loc_container, "showcase-left-center")
    assert get_title_tag_name(value_box2) == "p"
    value_box2.expect_title("Primary theme w/o Fullscreen")
    value_box2.expect_value("Showcase left center")
    assert get_value_tag_name(value_box2) == "h5"
    assert get_value_box_bg_color(value_box2) == "rgb(0, 123, 194)"
    value_box2.expect_full_screen_available(False)

    value_box3 = ValueBox(page, "valuebox3")
    value_box3.expect_height(None)
    # verify showcase layout uses 'showcase_bottom()'
    expect_to_have_class(value_box3.loc_container, "showcase-bottom")
    assert get_title_tag_name(value_box3) == "span"
    value_box3.expect_title("No theme w/ Fullscreen")
    value_box3.expect_value("Showcase bottom")
    assert get_value_tag_name(value_box3) == "h3"
    value_box3.expect_full_screen_available(True)
    assert get_value_box_bg_color(value_box3) == "rgb(255, 255, 255)"

    value_box4 = ValueBox(page, "valuebox4")
    value_box4.expect_height(None)
    value_box4.expect_title("No showcase - w/o Fullscreen (default)")
    value_box4.expect_value("No theme - only defaults")
    assert get_title_tag_name(value_box4) == "p"
    assert get_title_tag_name(value_box4) == "p"
    value_box4.expect_full_screen_available(False)
    assert get_value_box_bg_color(value_box4) == "rgb(255, 255, 255)"

    value_box5 = ValueBox(page, "valuebox5")
    value_box5.expect_height("500px")
    assert get_title_tag_name(value_box5) == "p"
    value_box5.expect_title("No showcase w/ showcase layout")
    value_box5.expect_value("Red text - fill is False")
    assert get_value_tag_name(value_box5) == "p"
    value_box5.expect_full_screen_available(False)
    assert get_value_box_bg_color(value_box5) == "rgb(255, 255, 255)"
    assert get_value_box_fg_color(value_box5) == "rgb(193, 0, 0)"
