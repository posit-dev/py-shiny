from conftest import ShinyAppProc
from playground import InputSlider, OutputTextVerbatim
from playwright.sync_api import Page


def test_input_slider_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s1 = InputSlider(page, "s1")
    s1.expect_label_to_have_text("regular")
    s1.expect_value("20")
    s1.expect_min_to_have_value("0")
    s1.expect_max_to_have_value("100")
    s1.expect_step_to_have_value("1")
    s1.expect_ticks_to_have_value("true")
    s1.expect_sep_to_have_value(",")
    s1.expect_pre_to_have_value(None)
    s1.expect_post_to_have_value(None)
    s1.expect_time_format_to_have_value(None)
    s1.expect_timezone_to_have_value(None)
    s1.expect_drag_range_to_have_value(None)

    OutputTextVerbatim(page, "txt1").expect_value("20")

    # TODO-future; Test more sliders
