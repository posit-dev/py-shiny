import re
import time

from conftest import ShinyAppProc
from controls import InputSlider, InputSliderRange, OutputTextVerbatim
from playwright.sync_api import Page

from shiny.types import MISSING


def test_slider_regular(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s0 = InputSlider(page, "s0")
    s0.expect_label("Integer")
    s0.expect_value("500")
    s0.expect_min("0")
    s0.expect_max("1000")
    s0.expect_step("1")
    s0.expect_ticks("false")
    s0.expect_sep(",")
    s0.expect_pre(None)
    s0.expect_post(None)
    s0.expect_time_format(None)
    s0.expect_timezone(None)
    s0.expect_drag_range(None)
    s0.expect_animate(exists=False)
    OutputTextVerbatim(page, "txt0").expect_value("500")

    new_val = "20"
    s0.set(new_val)
    s0.expect_value(new_val)
    OutputTextVerbatim(page, "txt0").expect_value(new_val)


def test_slider_range(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s1 = InputSliderRange(page, "s1")
    s1.expect_label("Range")
    s1.expect_value(("200", "500"))
    s1.expect_min("1")
    s1.expect_max("1000")
    s1.expect_step("1")
    s1.expect_ticks("false")
    s1.expect_sep(",")
    s1.expect_pre(None)
    s1.expect_post(None)
    s1.expect_time_format(None)
    s1.expect_timezone(None)
    s1.expect_drag_range("true")
    s1.expect_animate(exists=False)
    OutputTextVerbatim(page, "txt1").expect_value("(200, 500)")

    new_val = ("605", "840")
    s1.set(new_val, max_err_values=1000)
    try:
        s1.expect_value((MISSING, MISSING))  # type: ignore
    except ValueError as e:
        assert re.search("tuple entries cannot", str(e))
    s1.expect_value((new_val[0], MISSING))
    s1.expect_value((MISSING, new_val[1]))
    s1.expect_value(new_val)
    OutputTextVerbatim(page, "txt1").expect_value(f"({new_val[0]}, {new_val[1]})")


def test_slider_custom_format(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s2 = InputSlider(page, "s2")
    s2.expect_label("Custom Format")
    s2.expect_value("$0")
    s2.expect_min("0")
    s2.expect_max("10000")
    s2.expect_step("2500")
    s2.expect_ticks("true")
    s2.expect_sep(",")
    s2.expect_pre("$")
    s2.expect_post(None)
    s2.expect_time_format(None)
    s2.expect_timezone(None)
    s2.expect_drag_range(None)
    s2.expect_animate_options(loop=True, interval=500)
    OutputTextVerbatim(page, "txt2").expect_value("0")

    s2.set("$7,500")
    s2.expect_value("$7,500")
    OutputTextVerbatim(page, "txt2").expect_value("7500")


def test_slider_loop(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    s3 = InputSlider(page, "s3")
    s3.expect_label("Looping Animation")
    s3.expect_value("1,000")
    s3.expect_min("1")
    s3.expect_max("2000")
    s3.expect_step("10")
    s3.expect_ticks("false")
    s3.expect_sep(",")
    s3.expect_pre(None)
    s3.expect_post(None)
    s3.expect_time_format(None)
    s3.expect_timezone(None)
    s3.expect_drag_range(None)
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
    s4.expect_label("Single Animation")
    s4.expect_value("1")
    s4.expect_min("0")
    s4.expect_max("5")
    s4.expect_step("1")
    s4.expect_ticks("false")
    s4.expect_sep(",")
    s4.expect_pre(None)
    s4.expect_post(None)
    s4.expect_time_format(None)
    s4.expect_timezone(None)
    s4.expect_drag_range(None)
    s4.expect_animate_options(loop=False, interval=100)
    OutputTextVerbatim(page, "txt4").expect_value("1")

    s4.click_play()
    s4.expect_value("5")
    s4.click_play()  # can click again!
    s4.expect_value("5")
