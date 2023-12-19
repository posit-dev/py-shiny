# pyright: reportUnknownMemberType=false

from conftest import ShinyAppProc, create_example_fixture
from controls import (
    MISSING,
    InputCheckbox,
    InputCheckboxGroup,
    InputDate,
    InputDateRange,
    InputNumeric,
    InputRadioButtons,
    InputSelect,
    InputSlider,
    InputSliderRange,
    InputText,
)
from playwright.sync_api import Page, expect

inputs_update_app = create_example_fixture("inputs-update")


def check_vals(page: Page, label: str, num: int):
    opt_labels = [f"option label {num} {type}" for type in ["A", "B"]]
    opt_vals = [f"option-{num}-{type}" for type in ["A", "B"]]

    text = InputText(page, "inText")
    text.expect_label(f"New {label}")
    text.expect_value(f"New text {num}")

    innum = InputNumeric(page, "inNumber")
    innum.expect_label("Number input:")
    innum.expect_value(str(num))

    innum2 = InputNumeric(page, "inNumber2")
    innum2.expect_label(f"Number {label}")
    innum2.expect_value(str(num))

    slider = InputSlider(page, "inSlider")
    slider.expect_label(f"Slider {label}")
    slider.expect_value(str(num))

    slider2 = InputSliderRange(page, "inSlider2")
    slider2.expect_label("Slider input 2:")
    slider2.expect_value((str(num - 1), str(num + 1)))

    slider3 = InputSliderRange(page, "inSlider3")
    slider3.expect_value((MISSING, str(num + 2)))
    slider3.expect_label("Slider input 3:")

    date = InputDate(page, "inDate")
    date.expect_label(f"Date {label}")
    date.expect_value(f"2013-04-{num:02}")

    date_range_input = InputDateRange(page, "inDateRange")
    date_range_input.expect_label(f"Date range {label}")
    date_range_input.date_start.expect_value(f"2013-01-{num:02}")
    date_range_input.date_end.expect_value(f"2013-12-{num:02}")
    # TODO-future; Check min/max date
    # min=date(2001, 1, num),
    # max=date(2030, 1, num),

    cb = InputCheckbox(page, "inCheckbox")
    cb.expect_label("Checkbox input")
    cb.expect_checked((num % 2) == 1)

    cb_grp_input = InputCheckboxGroup(page, "inCheckboxGroup")
    cb_grp_input.expect_label(f"Checkbox group {label}")
    cb_grp_input.expect_choices(opt_vals)
    cb_grp_input.expect_choice_labels(opt_labels)
    cb_grp_input.expect_selected([opt_vals[0]])

    radio_btns_input = InputRadioButtons(page, "inRadio")
    radio_btns_input.expect_label(f"Radio {label}")
    radio_btns_input.expect_choice_labels(opt_labels)
    radio_btns_input.expect_choices(opt_vals)
    radio_btns_input.expect_selected(opt_vals[0])

    select = InputSelect(page, "inSelect")
    select.expect_label(f"Select {label}")
    select.expect_choice_labels(opt_labels)
    select.expect_choices(opt_vals)
    select.expect_selected(opt_vals[0])

    selectize = InputSelect(page, "inSelect2")
    selectize.expect_label(f"Select label {label}")
    selectize.expect_choices(opt_vals)
    selectize.expect_selected(opt_vals[1])

    # TODO-future: proper tab output classes
    panel1_is_visible = (num % 2) == 0
    panel1_expect = expect(page.locator('div[data-value="panel1"]'))
    panel2_expect = expect(page.locator('div[data-value="panel2"]'))
    if panel1_is_visible:
        panel1_expect.to_be_visible()
        panel2_expect.not_to_be_visible()
        panel1_expect.to_have_text("This is the first panel.")
    else:
        panel1_expect.not_to_be_visible()
        panel2_expect.to_be_visible()
        panel2_expect.to_have_text("This is the second panel.")


def test_updates(page: Page, inputs_update_app: ShinyAppProc):
    page.goto(inputs_update_app.url)

    for n in [9, 10]:
        label = f"LABEL {n} TEXT"
        InputText(page, "control_label").set(label)
        InputSlider(page, "control_num").set(str(n))
        check_vals(page, label, n)
