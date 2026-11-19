"""
Tests for `input_checkbox_group()` / `input_radio_buttons()` and their `update_*()`
counterparts, plus the choice-value normalization they share with the select inputs.

The `update_*()` functions must coerce choice values to strings the same way the input
constructors do, so that `choices={0: "a"}, selected=[0]` behaves identically to
`choices={"0": "a"}, selected=["0"]` (https://github.com/posit-dev/py-shiny/issues/2272).
"""

from __future__ import annotations

import json
from typing import Any, cast

import pytest
from htmltools import TagChild, TagList

from shiny import ui
from shiny.express._stub_session import ExpressStubSession
from shiny.session import Session, session_context
from shiny.session._session import RenderedDeps

CHOICES_INT: dict[int, str] = {0: "a", 1: "b", 2: "c"}
CHOICES_STR: dict[str, str] = {"0": "a", "1": "b", "2": "c"}


class _MessageCapturingSession(ExpressStubSession):
    """Stub session that records `send_input_message()` payloads and renders UI."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[dict[str, object]] = []

    def send_input_message(self, id: str, message: dict[str, object]) -> None:
        # `AppSession._send_message()` runs the payload through `json.dumps()`, so a
        # value that is not serializable fails at runtime rather than here. Assert it
        # up front so the tests cover the wire format, not just the dict.
        json.dumps(message)
        self.messages.append(message)

    def _process_ui(self, ui: TagChild) -> RenderedDeps:
        return {"deps": [], "html": TagList(ui).get_html_string()}


@pytest.fixture
def session() -> _MessageCapturingSession:
    return _MessageCapturingSession()


def _send(
    session: _MessageCapturingSession, fn: Any, **kwargs: Any
) -> dict[str, object]:
    with session_context(cast(Session, session)):
        fn("x", **kwargs)
    assert len(session.messages) == 1
    return session.messages.pop()


def _checked_count(html: str) -> int:
    return html.count('checked="checked"')


# ============================================================================
# input_checkbox_group() / input_radio_buttons(): int values work today
# ============================================================================
def test_input_checkbox_group_int_values_match_str_values():
    int_html = ui.input_checkbox_group(
        "x", label="L", choices=CHOICES_INT, selected=[0, 2]
    ).get_html_string()
    str_html = ui.input_checkbox_group(
        "x", label="L", choices=CHOICES_STR, selected=["0", "2"]
    ).get_html_string()
    assert int_html == str_html
    assert _checked_count(int_html) == 2


def test_input_radio_buttons_int_values_match_str_values():
    int_html = ui.input_radio_buttons(
        "x", label="L", choices=CHOICES_INT, selected=1
    ).get_html_string()
    str_html = ui.input_radio_buttons(
        "x", label="L", choices=CHOICES_STR, selected="1"
    ).get_html_string()
    assert int_html == str_html


@pytest.mark.parametrize(
    "choices, selected",
    [
        # The mixed cases are why normalization lives in the shared pipeline rather
        # than only on the outgoing message: coercing just the payload would leave the
        # options markup with nothing marked checked.
        ({0: "a", 1: "b"}, ["0"]),
        ({"0": "a", "1": "b"}, [0]),
    ],
)
def test_input_checkbox_group_mixed_value_types(
    choices: dict[Any, str], selected: list[Any]
):
    html = ui.input_checkbox_group(
        "x", label="L", choices=choices, selected=selected
    ).get_html_string()
    assert _checked_count(html) == 1
    assert 'value="0"' in html


def test_input_checkbox_group_numerically_equal_selected():
    # `str(1.0)` is `"1.0"`, so an integral float is matched against the integer it
    # names as well, and renders as the `"1"` the client will match on. R Shiny gets
    # this case for free, since `as.character(1.0)` is `"1"`.
    html = ui.input_checkbox_group(
        "x", label="L", choices={1: "a", 2: "b"}, selected=[1.0]
    ).get_html_string()
    assert _checked_count(html) == 1
    assert 'value="1" checked="checked"' in html


def test_bool_selected_does_not_name_an_int_choice(
    session: _MessageCapturingSession,
):
    # Matching is on the string form, so `True` does not name the choice value `1` even
    # though `True == 1`. This matches R Shiny, where `"TRUE"` and `"1"` differ.
    html = ui.input_radio_buttons(
        "x", label="L", choices={1: "one"}, selected=True
    ).get_html_string()
    assert _checked_count(html) == 0

    msg = _send(session, ui.update_radio_buttons, choices={1: "one"}, selected=True)
    assert msg["value"] == "True"


def test_choices_must_not_be_a_bare_string():
    # A `str` is a `Sequence[str]`, so it satisfies the `choices` annotation; iterating
    # it would silently turn each character into its own choice.
    for input_fn in (ui.input_checkbox_group, ui.input_radio_buttons, ui.input_select):
        with pytest.raises(TypeError, match="must be a list, tuple, or dict"):
            input_fn("x", label="L", choices=cast(Any, "abc"))


def test_choice_values_are_rendered_for_falsy_types():
    # htmltools omits an attribute whose value is `None`/`False` and renders `True` as
    # `value=""`, so without the `str()` coercion these options would carry no usable
    # value and the browser would report the default `"on"`.
    html = ui.input_checkbox_group(
        "x", label="L", choices={None: "n", False: "f", True: "t"}
    ).get_html_string()
    assert 'value="None"' in html
    assert 'value="False"' in html
    assert 'value="True"' in html


def test_choice_values_colliding_as_strings_raise():
    # Keying on `str()` would otherwise silently drop one of these options.
    with pytest.raises(ValueError, match="Duplicate choice value '0'"):
        ui.input_checkbox_group("x", label="L", choices={0: "zero", "0": "oh"})

    with pytest.raises(ValueError, match="Duplicate choice value '0'"):
        ui.input_checkbox_group("x", label="L", choices=[0, "0"])


def test_input_radio_buttons_empty_choices_raise():
    # A radio group with no explicit `selected` checks its first choice, so there has to
    # be one. This used to be an `IndexError` from inside a private helper.
    with pytest.raises(ValueError, match="`choices` cannot be empty"):
        ui.input_radio_buttons("x", label="L", choices=[])


def test_input_radio_buttons_selected_shapes():
    # `selected=None` falls back to the first choice; an explicitly empty `selected` is a
    # request for nothing checked and must stay that way.
    assert (
        _checked_count(
            ui.input_radio_buttons("x", label="L", choices=["a", "b"]).get_html_string()
        )
        == 1
    )
    assert (
        _checked_count(
            ui.input_radio_buttons(
                "x", label="L", choices=["a", "b"], selected=[]
            ).get_html_string()
        )
        == 0
    )


# ============================================================================
# update_checkbox_group(): the wire payload must match the string-valued one
# ============================================================================
def test_update_checkbox_group_int_values_match_str_values(
    session: _MessageCapturingSession,
):
    int_msg = _send(
        session,
        ui.update_checkbox_group,
        choices=CHOICES_INT,
        selected=list(CHOICES_INT.keys()),
    )
    str_msg = _send(
        session,
        ui.update_checkbox_group,
        choices=CHOICES_STR,
        selected=list(CHOICES_STR.keys()),
    )
    assert int_msg == str_msg
    # The client matches `value` against the HTML `value` attributes, which are
    # always strings.
    assert int_msg["value"] == ["0", "1", "2"]
    # Pin the options markup absolutely too: comparing the two payloads alone cannot
    # catch a bug in `_generate_options()`, since both sides would shift together.
    options = int_msg["options"]
    assert isinstance(options, str)
    assert _checked_count(options) == 3
    assert 'value="0" checked="checked"' in options


def test_update_checkbox_group_int_selected_without_choices(
    session: _MessageCapturingSession,
):
    msg = _send(session, ui.update_checkbox_group, selected=[0, 2])
    assert msg == {"value": ["0", "2"]}


def test_update_checkbox_group_selected_tuple_becomes_list_of_str(
    session: _MessageCapturingSession,
):
    msg = _send(session, ui.update_checkbox_group, selected=(0, 1))
    assert msg == {"value": ["0", "1"]}


def test_update_checkbox_group_scalar_selected_stays_scalar(
    session: _MessageCapturingSession,
):
    # A scalar `selected` must not become a list -- the client handles both, but
    # the shape should round-trip unchanged (apart from the `str()` coercion).
    msg = _send(session, ui.update_checkbox_group, selected=1)
    assert msg == {"value": "1"}


@pytest.mark.parametrize(
    "selected, expected",
    [
        ({0: "a", 1: "b"}.keys(), ["0", "1"]),
        ({0}, ["0"]),
        ((i for i in [0, 1]), ["0", "1"]),
        (range(2), ["0", "1"]),
    ],
)
def test_update_checkbox_group_accepts_any_iterable_selected(
    session: _MessageCapturingSession, selected: Any, expected: list[str]
):
    # These are iterable but not `list`/`tuple`. Treating them as scalars would stringify
    # them to an unusable `repr` (`"dict_keys([0, 1])"`) that matches no option.
    msg = _send(session, ui.update_checkbox_group, selected=selected)
    assert msg == {"value": expected}


def test_update_checkbox_group_inline_is_preserved_when_requested(
    session: _MessageCapturingSession,
):
    msg = _send(session, ui.update_checkbox_group, choices=["a", "b"], inline=True)
    options = msg["options"]
    assert isinstance(options, str)
    assert "checkbox-inline" in options


# ============================================================================
# update_radio_buttons(): same defect, same file
# ============================================================================
def test_update_radio_buttons_int_values_match_str_values(
    session: _MessageCapturingSession,
):
    int_msg = _send(session, ui.update_radio_buttons, choices=CHOICES_INT, selected=1)
    str_msg = _send(session, ui.update_radio_buttons, choices=CHOICES_STR, selected="1")
    assert int_msg == str_msg
    assert int_msg["value"] == "1"


def test_update_radio_buttons_int_selected_without_choices(
    session: _MessageCapturingSession,
):
    msg = _send(session, ui.update_radio_buttons, selected=2)
    assert msg == {"value": "2"}


@pytest.mark.parametrize("selected", [["a"], ("a",)])
def test_update_radio_buttons_one_element_selected_unwraps(
    session: _MessageCapturingSession, selected: Any
):
    # The radio binding's `setValue()` hands a non-empty array to `$escape()`, which
    # calls `.replace()` on it and throws, so the value has to reach it as a scalar.
    # Shiny for R arrives at the same place: `as.character()` on a length-1 vector
    # reaches the client as a JSON scalar.
    msg = _send(session, ui.update_radio_buttons, selected=selected)
    assert msg == {"value": "a"}


def test_update_radio_buttons_rejects_multiple_selected(
    session: _MessageCapturingSession,
):
    # A radio group can only show one of them. Quietly keeping the first would discard
    # the rest, which is the same silent data loss the duplicate-choice check exists to
    # prevent.
    with pytest.raises(ValueError, match="must name a single choice"):
        _send(session, ui.update_radio_buttons, selected=["a", "b"])


def test_update_radio_buttons_empty_choices_clears_the_group(
    session: _MessageCapturingSession,
):
    # The shared `_note` on the `update_*` functions documents `choices=[]` as the way
    # to clear the set of choices. For radio buttons that raised instead, because an
    # empty group has no first option to fall back on. The payload must now match what
    # `update_checkbox_group()` sends for the same call.
    radio = _send(session, ui.update_radio_buttons, choices=[])
    checkbox = _send(session, ui.update_checkbox_group, choices=[])

    assert radio == checkbox
    assert radio == {"options": '<div class="shiny-options-group"></div>'}


def test_update_radio_buttons_empty_choices_keeps_an_explicit_selected(
    session: _MessageCapturingSession,
):
    msg = _send(session, ui.update_radio_buttons, choices=[], selected="a")
    assert msg["value"] == "a"


def test_update_radio_buttons_empty_selected_stays_a_list(
    session: _MessageCapturingSession,
):
    # `selected=[]` is the documented way to clear a selection, and an empty array is the
    # one array shape the radio binding special-cases. Collapsing it to `None` would drop
    # `value` from the message and leave the previous selection in place.
    msg = _send(session, ui.update_radio_buttons, selected=[])
    assert msg == {"value": []}


# ============================================================================
# `selected=None` must stay absent from the payload (drop_none)
# ============================================================================
def test_update_choice_input_none_selected_is_dropped(
    session: _MessageCapturingSession,
):
    msg = _send(session, ui.update_checkbox_group, label="New label")
    assert "value" not in msg


# ============================================================================
# The select inputs share the same normalization
# ============================================================================
def test_update_select_int_values_match_str_values(
    session: _MessageCapturingSession,
):
    int_msg = _send(session, ui.update_select, choices=CHOICES_INT, selected=[0])
    str_msg = _send(session, ui.update_select, choices=CHOICES_STR, selected=["0"])
    assert int_msg == str_msg
    # jQuery's `.val()` matches option values with a strict `===`, so an `int` here
    # would deselect everything.
    assert int_msg["value"] == ["0"]
    options = int_msg["options"]
    assert isinstance(options, str)
    assert 'value="0" selected' in options


def test_update_selectize_int_values_match_str_values(
    session: _MessageCapturingSession,
):
    msg = _send(session, ui.update_selectize, choices=CHOICES_INT, selected=0)
    assert msg["value"] == ["0"]


def test_input_select_int_values_match_str_values():
    int_html = ui.input_select(
        "x", label="L", choices=CHOICES_INT, selected=1
    ).get_html_string()
    str_html = ui.input_select(
        "x", label="L", choices=CHOICES_STR, selected="1"
    ).get_html_string()
    assert int_html == str_html


def test_input_select_optgroup_int_values():
    # Optgroup labels are not choice values, but the options nested inside are.
    html = ui.input_select(
        "x",
        label="L",
        choices={"Group": {0: "a", 1: "b"}},
        selected=1,
    ).get_html_string()
    assert '<optgroup label="Group">' in html
    assert 'value="1" selected' in html


def test_input_select_optgroup_label_colliding_with_a_choice_value_raises():
    # An optgroup label and a flat choice value share the top-level mapping, so one of
    # the two entries would otherwise disappear. The error says which.
    with pytest.raises(ValueError, match="the optgroup label 0 and the choice value"):
        # A top level that mixes an optgroup with a flat option is supported at
        # runtime, but no arm of `SelectChoicesArg` describes it.
        ui.input_select("x", label="L", choices=cast(Any, {0: {1: "one"}, "0": "flat"}))


def test_input_select_duplicate_values_across_optgroups_are_allowed():
    # Two groups may hold the same choice value. Duplicate `value` attributes are legal
    # HTML and R Shiny permits them; the browser reports only the value, so the options
    # are indistinguishable however the server renders them.
    html = ui.input_select(
        "x", label="L", choices={"A": {0: "zero"}, "B": {"0": "oh"}}, selected=0
    ).get_html_string()
    assert html.count('value="0" selected') == 2
