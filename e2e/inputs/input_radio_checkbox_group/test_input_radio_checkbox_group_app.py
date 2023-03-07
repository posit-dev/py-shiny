from __future__ import annotations

from conftest import ShinyAppProc
from controls import InputCheckboxGroup, InputRadioButtons, PatternOrStr
from playwright.sync_api import Page, expect


def test_input_checkbox_group_kitchen(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    radio1 = InputRadioButtons(page, "radio1")
    radio2 = InputRadioButtons(page, "radio2")
    check1 = InputCheckboxGroup(page, "check1")
    check2 = InputCheckboxGroup(page, "check2")

    def assert_radio_check(
        x: InputRadioButtons | InputCheckboxGroup,
        label: str,
        choices: list[PatternOrStr],
        choice_labels: list[PatternOrStr],
        selected: PatternOrStr | list[PatternOrStr],
        inline: bool,
    ) -> None:
        expect(x.loc_label).to_have_text(label)
        x.expect_label(label)
        x.expect_choices(choices)
        x.expect_choice_labels(choice_labels)
        if isinstance(x, InputRadioButtons):
            if not isinstance(selected, str):
                raise TypeError("selected must be a string for radio buttons")
            x.expect_selected(selected)
        else:
            if not isinstance(selected, list):
                raise TypeError("selected must be a list for checkbox groups")
            x.expect_selected(selected)
        x.expect_inline(inline)

    def assert_selected(
        r1: str, r2: str, c1: list[PatternOrStr], c2: list[PatternOrStr]
    ) -> None:
        assert_radio_check(
            radio1,
            "Radio 1:",
            ["a", "b", "c"],
            ["A", "B", "C"],
            r1,
            False,
        )
        assert_radio_check(
            radio2,
            "Radio 2 (inline):",
            ["d", "e", "f"],
            ["D", "E", "F"],
            r2,
            True,
        )
        assert_radio_check(
            check1,
            "Check 1:",
            ["red", "green", "blue"],
            ["RED", "GREEN", "BLUE"],
            c1,
            False,
        )
        assert_radio_check(
            check2,
            "Check 2 (inline):",
            ["magenta", "orange", "teal"],
            ["MAGENTA", "ORANGE", "TEAL"],
            c2,
            True,
        )

    assert_selected("a", "d", [], [])

    radio1.set("b")
    radio2.set("f")
    check1.set(["red", "blue"])
    check2.set(["orange", "teal"])

    assert_selected("b", "f", ["red", "blue"], ["orange", "teal"])


def test_locator_debugging(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    # Fail quickly
    timeout = 100

    # Non-existent div
    try:
        not_exist = InputRadioButtons(page, "does-not-exist")
        not_exist.expect_choices(["a", "b", "c"], timeout=timeout)
    except AssertionError as e:
        assert "expected to have count '1'" in str(e)
        assert "Actual value: 0" in str(e)

    check1 = InputCheckboxGroup(page, "check1")

    # Make sure it works
    check1.expect_choices(["red", "green", "blue"])
    # Too many
    try:
        check1.expect_choices(["red", "green", "blue", "test_value"], timeout=timeout)
    except AssertionError as e:
        assert "expected to have count '4'" in str(e)
        assert "Actual value: 3" in str(e)
    # Not enough
    try:
        check1.expect_choices(["red", "green"], timeout=timeout)
    except AssertionError as e:
        assert "expected to have count '2'" in str(e)
        assert "Actual value: 3" in str(e)
    # Wrong value
    try:
        check1.expect_choices(["red", "green", "test_value"], timeout=timeout)
    except AssertionError as e:
        assert "attribute 'test_value'" in str(e)
        assert "Actual value: blue" in str(e)


def test_locator_existance(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    # Fail quickly
    timeout = 100

    # Non-existent div
    try:
        not_exist = InputCheckboxGroup(page, "does-not-exist")
        not_exist.set(["green"], timeout=timeout)
    except AssertionError as e:
        assert "expected to have count '1'" in str(e)
        assert "Actual value: 0" in str(e)

    check1 = InputCheckboxGroup(page, "check1")

    # Make sure it works
    check1.set([])
    check1.expect_selected([])
    check1.set(["green"])
    check1.expect_selected(["green"])

    # Different value
    try:
        check1.set(["test_value"], timeout=timeout)
    except AssertionError as e:
        assert "expected to have count '1'" in str(e)
        assert "Actual value: 0" in str(e)

    # Extra value
    try:
        check1.set(["blue", "test_value"], timeout=timeout)
    except AssertionError as e:
        assert "expected to have count '1'" in str(e)
        assert "Actual value: 0" in str(e)

    check1.expect_selected(["green"])
