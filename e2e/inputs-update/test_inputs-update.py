# pyright: reportUnknownMemberType=false

from conftest import ShinyAppProc, create_example_fixture
from controls import (
    CheckboxGroupInput,
    CheckboxInput,
    DateInput,
    DateRangeInput,
    NumericInput,
    RadioButtonsInput,
    SliderInput,
    TextInput,
)
from playwright.sync_api import Page

inputs_update_app = create_example_fixture("inputs-update")


def check_vals(page: Page, label: str, num: int):
    TextInput(page, "inText").expect.to_have_value(f"New text {num}")
    NumericInput(page, "inNumber").expect.to_have_value(str(num))
    NumericInput(page, "inNumber2").expect.to_have_value(str(num))
    DateInput(page, "inDate").expect.to_have_value(f"2013-04-{num:02}")
    date_range_input = DateRangeInput(page, "inDateRange")
    date_range_input.expect_start.to_have_value(f"2013-01-{num:02}")
    date_range_input.expect_end.to_have_value(f"2013-12-{num:02}")
    if num % 2 == 0:
        CheckboxInput(page, "inCheckbox").expect.not_to_be_checked()
    else:
        CheckboxInput(page, "inCheckbox").expect.to_be_checked()

    cb_grp_input = CheckboxGroupInput(page, "inCheckboxGroup")
    cb_grp_input.locate_by_label(f"option label {num} A").wait_for(state="visible")
    cb_grp_input.locate_by_label(f"option label {num} B").wait_for(state="visible")

    radio_btns_input = RadioButtonsInput(page, "inRadio")
    radio_btns_input.locate_by_label(f"option label {num} A").wait_for(state="visible")
    radio_btns_input.locate_by_label(f"option label {num} B").wait_for(state="visible")

    # TODO: #inSelect, #inSelect2
    # TODO: Check labels of all controls


def test_updates(page: Page, inputs_update_app: ShinyAppProc):
    page.goto(inputs_update_app.url)

    SliderInput(page, "control_num").move_slider(0)
    check_vals(page, "LABEL TEXT", 1)

    SliderInput(page, "control_num").move_slider(0.052)
    check_vals(page, "LABEL TEXT", 2)
