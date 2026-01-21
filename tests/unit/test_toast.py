"""Tests for shiny/ui/_toast.py - toast notification functions."""

import warnings
from unittest.mock import MagicMock, patch

import pytest
from htmltools import TagList, tags

from shiny.ui._toast import (
    Toast,
    ToastHeader,
    _normalize_toast_position,
    _normalize_toast_type,
    _toast_random_id,
    hide_toast,
    show_toast,
    toast,
    toast_header,
)


# =============================================================================
# Helper: Create mock session
# =============================================================================
def create_mock_session():
    """Create a mock session object for testing toast functions."""
    session = MagicMock()
    session._process_ui = MagicMock(side_effect=lambda x: {"html": str(x), "deps": []})
    session._send_message_sync = MagicMock()
    return session


# =============================================================================
# Tests for toast() function
# =============================================================================
class TestToastFunction:
    def test_basic_toast(self):
        """Test basic toast creation."""
        t = toast("Hello, World!")
        assert isinstance(t, Toast)
        assert t.closable is True

    def test_toast_with_header_string(self):
        """Test toast with string header (auto-converted)."""
        t = toast("Body content", header="My Header")
        assert isinstance(t.header, ToastHeader)

    def test_toast_with_header_object(self):
        """Test toast with ToastHeader object."""
        hdr = toast_header("Custom Header")
        t = toast("Body content", header=hdr)
        assert t.header is hdr

    def test_toast_with_icon(self):
        """Test toast with icon."""
        t = toast("Message", icon=tags.i(class_="fa fa-info"))
        assert t.icon is not None

    def test_toast_with_custom_id(self):
        """Test toast with custom ID."""
        t = toast("Message", id="my-toast-id")
        assert t.id == "my-toast-id"

    def test_toast_type_primary(self):
        """Test toast with primary type."""
        t = toast("Message", type="primary")
        assert t.type == "primary"

    def test_toast_type_error_normalized(self):
        """Test toast with error type (normalized to danger)."""
        t = toast("Message", type="error")
        assert t.type == "danger"

    def test_toast_type_success(self):
        """Test toast with success type."""
        t = toast("Message", type="success")
        assert t.type == "success"

    def test_toast_type_warning(self):
        """Test toast with warning type."""
        t = toast("Message", type="warning")
        assert t.type == "warning"

    def test_toast_duration_default(self):
        """Test toast with default duration (5 seconds)."""
        t = toast("Message")
        assert t.duration == 5000  # 5 seconds * 1000

    def test_toast_duration_custom(self):
        """Test toast with custom duration."""
        t = toast("Message", duration_s=10)
        assert t.duration == 10000

    def test_toast_duration_none(self):
        """Test toast with no auto-hide (None duration)."""
        t = toast("Message", duration_s=None)
        assert t.duration is None
        assert t.autohide is False

    def test_toast_duration_zero(self):
        """Test toast with zero duration (no auto-hide)."""
        t = toast("Message", duration_s=0)
        assert t.duration == 0
        assert t.autohide is False

    def test_toast_position_string(self):
        """Test toast with string position."""
        t = toast("Message", position="top-right")
        assert t.position == "top-right"

    def test_toast_position_list(self):
        """Test toast with list position."""
        t = toast("Message", position=["top", "left"])
        assert t.position == "top-left"

    def test_toast_position_tuple(self):
        """Test toast with tuple position."""
        t = toast("Message", position=("bottom", "center"))
        assert t.position == "bottom-center"

    def test_toast_closable_true(self):
        """Test toast with closable=True."""
        t = toast("Message", closable=True)
        assert t.closable is True

    def test_toast_closable_false(self):
        """Test toast with closable=False."""
        t = toast("Message", closable=False)
        assert t.closable is False

    def test_toast_with_kwargs(self):
        """Test toast with additional kwargs."""
        t = toast("Message", class_="custom-class", data_custom="value")
        assert "class_" in t.attribs or "class" in t.attribs


# =============================================================================
# Tests for toast_header() function
# =============================================================================
class TestToastHeader:
    def test_basic_header(self):
        """Test basic toast header creation."""
        hdr = toast_header("My Title")
        assert isinstance(hdr, ToastHeader)

    def test_header_with_icon(self):
        """Test toast header with icon."""
        hdr = toast_header("Title", icon=tags.i(class_="fa fa-bell"))
        assert hdr.icon is not None

    def test_header_with_status(self):
        """Test toast header with status text."""
        hdr = toast_header("Title", status="just now")
        assert hdr.status == "just now"

    def test_header_with_all_params(self):
        """Test toast header with all parameters."""
        hdr = toast_header(
            "Title",
            icon=tags.i(class_="icon"),
            status="5 mins ago",
            class_="custom-header",
        )
        assert hdr.icon is not None
        assert hdr.status == "5 mins ago"

    def test_header_tagify(self):
        """Test toast header tagify method."""
        hdr = toast_header("Title")
        tag = hdr.tagify()
        html = str(tag)
        assert "toast-header" in html

    def test_header_tagify_with_close_button(self):
        """Test toast header tagify with close button."""
        hdr = toast_header("Title")
        close_btn = tags.button(type="button", class_="btn-close")
        tag = hdr.tagify(close_button=close_btn)
        html = str(tag)
        assert "btn-close" in html


# =============================================================================
# Tests for Toast class
# =============================================================================
class TestToastClass:
    def test_toast_tagify(self):
        """Test Toast.tagify() method."""
        t = toast("Message")
        tag = t.tagify()
        html = str(tag)
        assert "toast" in html
        assert "toast-body" in html

    def test_toast_tagify_with_header(self):
        """Test Toast.tagify() with header."""
        t = toast("Message", header="Title")
        tag = t.tagify()
        html = str(tag)
        assert "toast-header" in html

    def test_toast_tagify_danger_type_accessibility(self):
        """Test Toast.tagify() with danger type has correct accessibility."""
        t = toast("Error message", type="danger")
        tag = t.tagify()
        html = str(tag)
        assert 'role="alert"' in html
        assert 'aria-live="assertive"' in html

    def test_toast_tagify_normal_type_accessibility(self):
        """Test Toast.tagify() with normal type has correct accessibility."""
        t = toast("Info message", type="info")
        tag = t.tagify()
        html = str(tag)
        assert 'role="status"' in html
        assert 'aria-live="polite"' in html

    def test_toast_as_payload(self):
        """Test Toast.as_payload() method."""
        session = create_mock_session()
        t = toast("Message", id="test-toast")
        payload = t.as_payload(session)

        assert payload is not None
        assert payload["id"] == "test-toast"
        assert "html" in payload
        assert "deps" in payload
        assert "position" in payload
        assert "autohide" in payload

    def test_toast_as_payload_empty_returns_none(self):
        """Test Toast.as_payload() with no content returns None."""
        session = create_mock_session()
        t = Toast(body=TagList(), header=None)
        payload = t.as_payload(session)
        assert payload is None


# =============================================================================
# Tests for show_toast()
# =============================================================================
class TestShowToast:
    def test_show_toast_with_toast_object(self):
        """Test show_toast with Toast object."""
        session = create_mock_session()
        t = toast("Hello!", id="my-toast")

        with patch("shiny.ui._toast.require_active_session", return_value=session):
            result = show_toast(t, session=session)

        assert result == "my-toast"
        session._send_message_sync.assert_called_once()

    def test_show_toast_with_string(self):
        """Test show_toast with plain string."""
        session = create_mock_session()

        with patch("shiny.ui._toast.require_active_session", return_value=session):
            result = show_toast("Simple message", session=session)

        assert isinstance(result, str)
        session._send_message_sync.assert_called_once()

    def test_show_toast_with_taglist(self):
        """Test show_toast with TagList."""
        session = create_mock_session()

        with patch("shiny.ui._toast.require_active_session", return_value=session):
            result = show_toast(TagList(tags.strong("Bold"), " text"), session=session)

        assert isinstance(result, str)
        session._send_message_sync.assert_called_once()

    def test_show_toast_empty_warns(self):
        """Test show_toast with empty toast shows warning."""
        session = create_mock_session()
        t = Toast(body=TagList(), header=None)

        with patch("shiny.ui._toast.require_active_session", return_value=session):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = show_toast(t, session=session)

                assert len(w) == 1
                assert "no content" in str(w[0].message).lower()
                assert result == ""

    def test_show_toast_message_structure(self):
        """Test show_toast sends correct message structure."""
        session = create_mock_session()
        t = toast("Test message")

        with patch("shiny.ui._toast.require_active_session", return_value=session):
            show_toast(t, session=session)

        call_args = session._send_message_sync.call_args[0][0]
        assert "custom" in call_args
        assert "bslib.show-toast" in call_args["custom"]


# =============================================================================
# Tests for hide_toast()
# =============================================================================
class TestHideToast:
    def test_hide_toast_with_string_id(self):
        """Test hide_toast with string ID."""
        session = create_mock_session()

        with patch("shiny.ui._toast.require_active_session", return_value=session):
            result = hide_toast("my-toast-id", session=session)

        assert result == "my-toast-id"
        session._send_message_sync.assert_called_once()

    def test_hide_toast_with_toast_object(self):
        """Test hide_toast with Toast object that has ID."""
        session = create_mock_session()
        t = toast("Message", id="toast-with-id")

        with patch("shiny.ui._toast.require_active_session", return_value=session):
            result = hide_toast(t, session=session)

        assert result == "toast-with-id"

    def test_hide_toast_no_id_raises(self):
        """Test hide_toast with Toast without ID raises error."""
        session = create_mock_session()
        t = Toast(body=TagList("Content"), id=None)

        with patch("shiny.ui._toast.require_active_session", return_value=session):
            with pytest.raises(ValueError, match="Cannot hide toast without an ID"):
                hide_toast(t, session=session)

    def test_hide_toast_message_structure(self):
        """Test hide_toast sends correct message structure."""
        session = create_mock_session()

        with patch("shiny.ui._toast.require_active_session", return_value=session):
            hide_toast("test-id", session=session)

        call_args = session._send_message_sync.call_args[0][0]
        assert "custom" in call_args
        assert "bslib.hide-toast" in call_args["custom"]
        assert call_args["custom"]["bslib.hide-toast"]["id"] == "test-id"


# =============================================================================
# Tests for _normalize_toast_type()
# =============================================================================
class TestNormalizeToastType:
    def test_normalize_none(self):
        """Test normalizing None type."""
        assert _normalize_toast_type(None) is None

    def test_normalize_error_to_danger(self):
        """Test error is normalized to danger."""
        assert _normalize_toast_type("error") == "danger"

    def test_normalize_primary_unchanged(self):
        """Test primary type unchanged."""
        assert _normalize_toast_type("primary") == "primary"

    def test_normalize_success_unchanged(self):
        """Test success type unchanged."""
        assert _normalize_toast_type("success") == "success"

    def test_normalize_warning_unchanged(self):
        """Test warning type unchanged."""
        assert _normalize_toast_type("warning") == "warning"

    def test_normalize_danger_unchanged(self):
        """Test danger type unchanged."""
        assert _normalize_toast_type("danger") == "danger"


# =============================================================================
# Tests for _normalize_toast_position()
# =============================================================================
class TestNormalizeToastPosition:
    def test_normalize_none_returns_default(self):
        """Test None returns default position."""
        assert _normalize_toast_position(None) == "bottom-right"

    def test_normalize_empty_string_returns_default(self):
        """Test empty string returns default position."""
        assert _normalize_toast_position("") == "bottom-right"

    def test_normalize_kebab_case(self):
        """Test kebab-case position."""
        assert _normalize_toast_position("top-right") == "top-right"

    def test_normalize_space_separated(self):
        """Test space-separated position."""
        assert _normalize_toast_position("top left") == "top-left"

    def test_normalize_list(self):
        """Test list position."""
        assert _normalize_toast_position(["bottom", "center"]) == "bottom-center"

    def test_normalize_tuple(self):
        """Test tuple position."""
        assert _normalize_toast_position(("middle", "right")) == "middle-right"

    def test_normalize_reverse_order(self):
        """Test reverse order (horizontal first)."""
        assert _normalize_toast_position(["left", "top"]) == "top-left"

    def test_normalize_case_insensitive(self):
        """Test case insensitivity."""
        assert _normalize_toast_position("TOP-RIGHT") == "top-right"

    def test_normalize_all_positions(self):
        """Test all valid position combinations."""
        valid_verticals = ["top", "middle", "bottom"]
        valid_horizontals = ["left", "center", "right"]

        for v in valid_verticals:
            for h in valid_horizontals:
                result = _normalize_toast_position(f"{v}-{h}")
                assert result == f"{v}-{h}"

    def test_normalize_invalid_component_raises(self):
        """Test invalid position component raises error."""
        with pytest.raises(ValueError, match="Invalid position component"):
            _normalize_toast_position("top-invalid")

    def test_normalize_multiple_vertical_raises(self):
        """Test multiple vertical components raises error."""
        with pytest.raises(ValueError, match="multiple vertical"):
            _normalize_toast_position("top bottom left")

    def test_normalize_multiple_horizontal_raises(self):
        """Test multiple horizontal components raises error."""
        with pytest.raises(ValueError, match="multiple horizontal"):
            _normalize_toast_position("top left right")

    def test_normalize_missing_vertical_raises(self):
        """Test missing vertical component raises error."""
        with pytest.raises(ValueError, match="vertical component"):
            _normalize_toast_position("left")

    def test_normalize_missing_horizontal_raises(self):
        """Test missing horizontal component raises error."""
        with pytest.raises(ValueError, match="horizontal component"):
            _normalize_toast_position("top")


# =============================================================================
# Tests for _toast_random_id()
# =============================================================================
class TestToastRandomId:
    def test_random_id_format(self):
        """Test random ID has correct format."""
        id = _toast_random_id()
        assert id.startswith("bslib-toast-")
        assert len(id) > len("bslib-toast-")

    def test_random_ids_unique(self):
        """Test random IDs are unique."""
        ids = [_toast_random_id() for _ in range(100)]
        assert len(set(ids)) == 100  # All unique
