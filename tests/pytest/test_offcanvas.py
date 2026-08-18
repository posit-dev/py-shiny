from __future__ import annotations

import warnings
from typing import Any
from unittest.mock import MagicMock

import pytest
from htmltools import HTML, TagList, tags

from shiny import ui
from shiny.ui._offcanvas import Offcanvas

# ============================================================================
# Construction tests
# ============================================================================


def test_offcanvas_returns_offcanvas_instance():
    oc = ui.offcanvas(id="x")
    assert isinstance(oc, Offcanvas)


def test_offcanvas_kwargs_become_html_attrs():
    oc = ui.offcanvas(id="x", title="T", data_foo="bar")
    rendered = str(oc.tagify())
    assert 'data-foo="bar"' in rendered


# ============================================================================
# Placement mapping tests
# ============================================================================


@pytest.mark.parametrize(
    "placement, expected_class",
    [
        ("left", "offcanvas-start"),
        ("right", "offcanvas-end"),
        ("top", "offcanvas-top"),
        ("bottom", "offcanvas-bottom"),
        ("start", "offcanvas-start"),
        ("end", "offcanvas-end"),
    ],
)
def test_offcanvas_placement_class(placement: str, expected_class: str):
    oc = ui.offcanvas(id="x", title="T", placement=placement)  # type: ignore[arg-type]
    rendered = str(oc.tagify())
    assert expected_class in rendered


def test_offcanvas_invalid_placement_raises():
    with pytest.raises(ValueError, match="placement"):
        ui.offcanvas(id="x", placement="middle")  # type: ignore[arg-type]


# ============================================================================
# Size warning tests
# ============================================================================


def test_offcanvas_width_with_top_placement_warns():
    with pytest.warns(UserWarning, match="width"):
        ui.offcanvas(id="x", placement="top", width=300)


def test_offcanvas_height_with_left_placement_warns():
    with pytest.warns(UserWarning, match="height"):
        ui.offcanvas(id="x", placement="left", height="30vh")


# ============================================================================
# tagify() validation tests
# ============================================================================


def test_offcanvas_no_id_no_trigger_raises_on_tagify():
    oc = ui.offcanvas()
    with pytest.raises(ValueError, match="id.*trigger|trigger.*id"):
        oc.tagify()


def test_offcanvas_with_id_tagifies():
    oc = ui.offcanvas(id="x", title="T")
    result = oc.tagify()
    assert result is not None


def test_offcanvas_with_trigger_tagifies():
    oc = ui.offcanvas(trigger=tags.button("Open"), title="T")
    result = oc.tagify()
    assert result is not None


def test_offcanvas_no_title_no_aria_label_warns():
    oc = ui.offcanvas(id="x")
    with pytest.warns(UserWarning, match="aria-label"):
        oc.tagify()


def test_offcanvas_with_aria_label_no_warning():
    oc = ui.offcanvas(id="x", aria_label="My panel")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        oc.tagify()


# ============================================================================
# HTML structure tests
# ============================================================================


def test_offcanvas_title_renders_with_id():
    oc = ui.offcanvas(id="myid", title="My Title")
    rendered = str(oc.tagify())
    assert 'id="myid-title"' in rendered
    assert "offcanvas-title" in rendered
    assert 'aria-labelledby="myid-title"' in rendered


def test_offcanvas_close_button_true():
    oc = ui.offcanvas(id="x", title="T", close_button=True)
    rendered = str(oc.tagify())
    assert "btn-close" in rendered
    assert 'data-bs-dismiss="offcanvas"' in rendered


def test_offcanvas_close_button_false():
    oc = ui.offcanvas(id="x", title="T", close_button=False)
    rendered = str(oc.tagify())
    assert "btn-close" not in rendered


def test_offcanvas_header_omitted_when_no_title_and_no_close_button():
    oc = ui.offcanvas(id="x", aria_label="panel", close_button=False)
    rendered = str(oc.tagify())
    assert "offcanvas-header" not in rendered


def test_offcanvas_footer_rendered_when_provided():
    oc = ui.offcanvas(id="x", title="T", footer=tags.div("Footer content"))
    rendered = str(oc.tagify())
    assert "offcanvas-footer" in rendered
    assert "Footer content" in rendered


def test_offcanvas_footer_absent_when_not_provided():
    oc = ui.offcanvas(id="x", title="T")
    rendered = str(oc.tagify())
    assert "offcanvas-footer" not in rendered


# ============================================================================
# Backdrop / scroll / keyboard attribute tests
# ============================================================================


def test_offcanvas_backdrop_false():
    oc = ui.offcanvas(id="x", title="T", backdrop=False)
    rendered = str(oc.tagify())
    assert 'data-bs-backdrop="false"' in rendered


def test_offcanvas_backdrop_static():
    oc = ui.offcanvas(id="x", title="T", backdrop="static")
    rendered = str(oc.tagify())
    assert 'data-bs-backdrop="static"' in rendered


def test_offcanvas_backdrop_true_no_attr():
    oc = ui.offcanvas(id="x", title="T", backdrop=True)
    rendered = str(oc.tagify())
    assert "data-bs-backdrop" not in rendered


def test_offcanvas_scroll_true():
    oc = ui.offcanvas(id="x", title="T", scroll=True)
    rendered = str(oc.tagify())
    assert 'data-bs-scroll="true"' in rendered


def test_offcanvas_scroll_false_no_attr():
    oc = ui.offcanvas(id="x", title="T", scroll=False)
    rendered = str(oc.tagify())
    assert "data-bs-scroll" not in rendered


def test_offcanvas_keyboard_false():
    oc = ui.offcanvas(id="x", title="T", keyboard=False)
    rendered = str(oc.tagify())
    assert 'data-bs-keyboard="false"' in rendered


def test_offcanvas_keyboard_true_no_attr():
    oc = ui.offcanvas(id="x", title="T", keyboard=True)
    rendered = str(oc.tagify())
    assert "data-bs-keyboard" not in rendered


# ============================================================================
# Size CSS variable tests
# ============================================================================


def test_offcanvas_width_sets_css_var():
    oc = ui.offcanvas(id="x", title="T", placement="left", width=300)
    rendered = str(oc.tagify())
    assert "--bs-offcanvas-width:" in rendered
    assert "300" in rendered
    assert "px" in rendered


def test_offcanvas_height_sets_css_var():
    oc = ui.offcanvas(id="x", title="T", placement="top", height="30vh")
    rendered = str(oc.tagify())
    assert "--bs-offcanvas-height: 30vh" in rendered


def test_offcanvas_no_size_no_style():
    oc = ui.offcanvas(id="x", title="T")
    rendered = str(oc.tagify())
    assert "--bs-offcanvas-width" not in rendered
    assert "--bs-offcanvas-height" not in rendered


# ============================================================================
# Trigger wiring tests
# ============================================================================


def test_offcanvas_trigger_gets_data_bs_attrs():
    btn = tags.button("Open")
    oc = ui.offcanvas(id="myid", title="T", trigger=btn)
    result = oc.tagify()
    rendered = str(result)
    assert 'data-bs-toggle="offcanvas"' in rendered
    assert 'data-bs-target="#myid"' in rendered
    assert 'aria-controls="myid"' in rendered


def test_offcanvas_taglist_trigger_last_element_wired():
    btn1 = tags.span("Prefix")
    btn2 = tags.button("Open")
    trigger_list = TagList(btn1, btn2)
    oc = ui.offcanvas(id="myid", title="T", trigger=trigger_list)
    result = oc.tagify()
    rendered = str(result)
    assert 'data-bs-toggle="offcanvas"' in rendered
    assert 'data-bs-target="#myid"' in rendered
    assert 'aria-controls="myid"' in rendered


def test_offcanvas_with_trigger_returns_taglist():
    btn = tags.button("Open")
    oc = ui.offcanvas(id="myid", title="T", trigger=btn)
    result = oc.tagify()
    html = str(result)
    assert "bslib-offcanvas" in html
    assert "Open" in html


# ============================================================================
# show_offcanvas() dispatch tests
# ============================================================================


def _mock_session() -> MagicMock:
    def _ns(id: str) -> str:
        return id

    def _send_message_sync(msg: dict[str, Any]) -> None:
        messages_sent.append(msg)

    def _send_input_message(id: str, msg: dict[str, Any]) -> None:
        input_messages_sent.append((id, msg))

    def _on_flush(cb: Any, once: bool = True) -> None:
        cb()

    mock_session = MagicMock()
    mock_session.ns = MagicMock(side_effect=_ns)
    mock_session._process_ui = MagicMock(
        return_value={"html": "<div>test</div>", "deps": []}
    )
    messages_sent: list[dict[str, Any]] = []
    mock_session._send_message_sync = MagicMock(side_effect=_send_message_sync)
    mock_session._messages_sent = messages_sent
    input_messages_sent: list[tuple[str, dict[str, Any]]] = []
    mock_session.send_input_message = MagicMock(side_effect=_send_input_message)
    mock_session._input_messages_sent = input_messages_sent
    mock_session.on_flush = MagicMock(side_effect=_on_flush)
    return mock_session


def test_show_offcanvas_with_str_id_reveals_existing_panel():
    """show_offcanvas() with a bare string reveals an existing panel by id"""
    mock_session = _mock_session()

    result_id = ui.show_offcanvas("existing-panel", session=mock_session)

    assert result_id == "existing-panel"
    assert mock_session._input_messages_sent == [
        ("existing-panel", {"method": "toggle", "value": "show"})
    ]
    mock_session._send_message_sync.assert_not_called()


@pytest.mark.parametrize("bad_id", ["", "   ", "has space", "\ttab"])
def test_show_offcanvas_bad_string_raises(bad_id: str):
    """show_offcanvas() raises when the string looks like body text, not an id"""
    mock_session = _mock_session()

    with pytest.raises(ValueError, match="looks like body text"):
        ui.show_offcanvas(bad_id, session=mock_session)


def test_show_offcanvas_with_html_wraps_new_panel():
    """show_offcanvas() treats htmltools.HTML() as content, not an id"""
    mock_session = _mock_session()

    result_id = ui.show_offcanvas(
        HTML("<p>Rendered content.</p>"), session=mock_session
    )

    assert isinstance(result_id, str) and result_id != ""
    assert mock_session._send_message_sync.call_count == 1
    message = mock_session._messages_sent[0]
    payload = message["custom"]["bslib.show-offcanvas"]
    assert payload["temporary"] is True
    assert payload["id"] == result_id


def test_show_offcanvas_with_tag_wraps_new_panel():
    """show_offcanvas() wraps a bare Tag into a new anonymous offcanvas"""
    mock_session = _mock_session()

    result_id = ui.show_offcanvas(tags.p("Body content"), session=mock_session)

    assert mock_session._send_message_sync.call_count == 1
    message = mock_session._messages_sent[0]
    payload = message["custom"]["bslib.show-offcanvas"]
    assert payload["temporary"] is True
    assert payload["id"] == result_id


def test_show_offcanvas_with_offcanvas_object_unchanged():
    """show_offcanvas() with an Offcanvas object renders + shows it (existing behavior)"""
    mock_session = _mock_session()

    oc = ui.offcanvas("Body", title="T", id="my_panel")
    result_id = ui.show_offcanvas(oc, session=mock_session)

    assert result_id == "my_panel"
    assert mock_session._send_message_sync.call_count == 1
    message = mock_session._messages_sent[0]
    payload = message["custom"]["bslib.show-offcanvas"]
    assert payload["temporary"] is False
    assert payload["id"] == "my_panel"


def test_offcanvas_without_trigger_returns_tag():
    oc = ui.offcanvas(id="myid", title="T")
    result = oc.tagify()
    assert "bslib-offcanvas" in str(result)
