from conftest import ShinyAppProc
from playground import (
    InputCheckboxGroup,
    InputRadioButtons,
    PatternOrStr,
    TextValue,
    typing,
)
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
        choices: typing.List[str],
        choice_labels: typing.List[PatternOrStr],
        selected: str | typing.List[str],
        inline: bool,
    ) -> None:
        expect(x.loc_label).to_have_text(label)
        x.expect_label_to_have_text(label)
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
        r1: str, r2: str, c1: typing.List[str], c2: typing.List[str]
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
