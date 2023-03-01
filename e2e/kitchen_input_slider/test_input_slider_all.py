import re
import time

from conftest import ShinyAppProc
from playground import InputSlider, InputSliderRange, OutputTextVerbatim
from playwright.sync_api import Page


def test_slider_regular(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s0 = InputSlider(page, "s0")
    s0.expect_label_to_have_text("Integer")
    s0.expect_value("500")
    s0.expect_min_to_have_value("0")
    s0.expect_max_to_have_value("1000")
    s0.expect_step_to_have_value("1")
    s0.expect_ticks_to_have_value("true")
    s0.expect_sep_to_have_value(",")
    s0.expect_pre_to_have_value(None)
    s0.expect_post_to_have_value(None)
    s0.expect_time_format_to_have_value(None)
    s0.expect_timezone_to_have_value(None)
    s0.expect_drag_range_to_have_value(None)
    s0.expect_animate(exists=False)
    OutputTextVerbatim(page, "txt0").expect_value("500")

    new_val = "36"
    s0.set(new_val)
    s0.expect_value(new_val)
    OutputTextVerbatim(page, "txt0").expect_value(new_val)


def test_slider_range(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s1 = InputSliderRange(page, "s1")
    s1.expect_label_to_have_text("Range")
    s1.expect_value(("200", "500"))
    s1.expect_min_to_have_value("1")
    s1.expect_max_to_have_value("1000")
    s1.expect_step_to_have_value("1")
    s1.expect_ticks_to_have_value("true")
    s1.expect_sep_to_have_value(",")
    s1.expect_pre_to_have_value(None)
    s1.expect_post_to_have_value(None)
    s1.expect_time_format_to_have_value(None)
    s1.expect_timezone_to_have_value(None)
    s1.expect_drag_range_to_have_value("true")
    s1.expect_animate(exists=False)
    OutputTextVerbatim(page, "txt0").expect_value("500")

    new_val = ("605", "885")
    s1.set(new_val, max_err_values=1000)
    try:
        s1.expect_value((None, None))
    except ValueError as e:
        assert re.search("tuple entries cannot", str(e))
    s1.expect_value((new_val[0], None))
    s1.expect_value((None, new_val[1]))
    s1.expect_value(new_val)
    OutputTextVerbatim(page, "txt1").expect_value(f"({new_val[0]}, {new_val[1]})")


def test_slider_custom_format(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s2 = InputSlider(page, "s2")
    s2.expect_label_to_have_text("Custom Format")
    s2.expect_value("$0")
    s2.expect_min_to_have_value("0")
    s2.expect_max_to_have_value("10000")
    s2.expect_step_to_have_value("2500")
    s2.expect_ticks_to_have_value("true")
    s2.expect_sep_to_have_value(",")
    s2.expect_pre_to_have_value("$")
    s2.expect_post_to_have_value(None)
    s2.expect_time_format_to_have_value(None)
    s2.expect_timezone_to_have_value(None)
    s2.expect_drag_range_to_have_value(None)
    s2.expect_animate_options(loop=True, interval=500)
    OutputTextVerbatim(page, "txt2").expect_value("0")

    s2.set("$7,500")
    s2.expect_value("$7,500")
    OutputTextVerbatim(page, "txt2").expect_value("7500")


def test_slider_loop(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s3 = InputSlider(page, "s3")
    s3.expect_label_to_have_text("Looping Animation")
    s3.expect_value("1,000")
    s3.expect_min_to_have_value("1")
    s3.expect_max_to_have_value("2000")
    s3.expect_step_to_have_value("10")
    s3.expect_ticks_to_have_value("true")
    s3.expect_sep_to_have_value(",")
    s3.expect_pre_to_have_value(None)
    s3.expect_post_to_have_value(None)
    s3.expect_time_format_to_have_value(None)
    s3.expect_timezone_to_have_value(None)
    s3.expect_drag_range_to_have_value(None)
    s3.expect_animate_options(loop=True, interval=300)
    OutputTextVerbatim(page, "txt3").expect_value("1000")

    s3.set("1,441")
    s3.expect_value("1,441")
    OutputTextVerbatim(page, "txt3").expect_value("1441")

    # Play for a little bit
    s3.click_play()
    time.sleep(400 / 1000)
    s3.click_pause()
    # Make sure the value changed
    try:
        s3.expect_value("1,441", timeout=100)
    except AssertionError:
        pass


def test_slider_play(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s4 = InputSlider(page, "s4")
    s4.expect_label_to_have_text("Single Animation")
    s4.expect_value("1")
    s4.expect_min_to_have_value("0")
    s4.expect_max_to_have_value("5")
    s4.expect_step_to_have_value("1")
    s4.expect_ticks_to_have_value("true")
    s4.expect_sep_to_have_value(",")
    s4.expect_pre_to_have_value(None)
    s4.expect_post_to_have_value(None)
    s4.expect_time_format_to_have_value(None)
    s4.expect_timezone_to_have_value(None)
    s4.expect_drag_range_to_have_value(None)
    s4.expect_animate_options(loop=False, interval=100)
    OutputTextVerbatim(page, "txt4").expect_value("1")

    s4.click_play()
    s4.expect_value("5", timeout=1000)
    s4.click_play()  # can click again!
    s4.expect_value("5", timeout=1000)
