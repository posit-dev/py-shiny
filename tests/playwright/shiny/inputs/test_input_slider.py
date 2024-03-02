from conftest import ShinyAppProc, create_doc_example_core_fixture
from controls import InputSlider, OutputTextVerbatim
from playwright.sync_api import Page, expect

slider_app = create_doc_example_core_fixture("input_slider")
template_app = create_doc_example_core_fixture("template")


def test_input_slider_kitchen(page: Page, slider_app: ShinyAppProc) -> None:
    page.goto(slider_app.url)

    # page.set_default_timeout(1000)

    obs = InputSlider(page, "obs")

    expect(obs.loc_label).to_have_text("Number of bins:")

    obs.expect_tick_labels(None)
    obs.expect_value("30")

    obs.expect_animate(False)
    # obs.expect_animate_interval(500)
    # obs.expect_animate_loop(True)
    obs.expect_min("10")
    obs.expect_max("100")
    # obs.expect_from()
    obs.expect_step("1")
    obs.expect_ticks("false")
    obs.expect_sep(",")
    obs.expect_pre(None)
    obs.expect_post(None)
    # obs.expect_data_type()
    obs.expect_time_format(None)
    obs.expect_timezone(None)
    obs.expect_drag_range(None)

    obs.set("42")
    obs.expect_value("42")

    # obs.set_fraction((21.0 - 10.0) / (100.0 - 10.0))
    # obs.expect_value("21")

    # # Duplicate logic of next test. Only difference is `max_err_values=15`
    # try:
    #     obs.set("not-a-number", timeout=800)
    # except ValueError as e:
    #     values_found = '"10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", ...'
    #     assert values_found in str(
    #         e
    #     ), "Error message should contain the list of first 15 valid values"

    try:
        obs.set("not-a-number", timeout=800, max_err_values=4)
    except ValueError as e:
        values_found = '"10", "11", "12", "13", ...'
        assert values_found in str(
            e
        ), "Error message should contain the list of first 4 valid values"


def test_input_slider_output(page: Page, template_app: ShinyAppProc) -> None:
    page.goto(template_app.url)

    slider = InputSlider(page, "n")
    txt = OutputTextVerbatim(page, "txt")

    txt.expect_value("n*2 is 40")
    slider.expect_label("N")
    slider.expect_value("20")

    slider.set("42")
    slider.expect_value("42")

    txt.expect_value("n*2 is 84")
