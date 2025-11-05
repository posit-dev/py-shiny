import re
from typing import Any

import pytest

from shiny import ui
from shiny.ui._toast import Toast, ToastHeader, _normalize_toast_position

# ==============================================================================
# Position normalization tests
# ==============================================================================


def test_normalize_position_kebab_case():
    """Standard kebab-case format"""
    assert _normalize_toast_position("top-left") == "top-left"
    assert _normalize_toast_position("bottom-right") == "bottom-right"
    assert _normalize_toast_position("middle-center") == "middle-center"


def test_normalize_position_space_separated():
    """Space-separated format"""
    assert _normalize_toast_position("top left") == "top-left"
    assert _normalize_toast_position("bottom right") == "bottom-right"
    assert _normalize_toast_position("middle center") == "middle-center"


def test_normalize_position_reversed_order():
    """Reversed order (horizontal first, then vertical)"""
    assert _normalize_toast_position("left top") == "top-left"
    assert _normalize_toast_position("right bottom") == "bottom-right"
    assert _normalize_toast_position("center middle") == "middle-center"


def test_normalize_position_list_input():
    """List/tuple input"""
    assert _normalize_toast_position(["top", "left"]) == "top-left"
    assert _normalize_toast_position(["bottom", "right"]) == "bottom-right"
    assert _normalize_toast_position(["left", "top"]) == "top-left"
    assert _normalize_toast_position(("right", "bottom")) == "bottom-right"


def test_normalize_position_case_insensitive():
    """Case insensitivity"""
    assert _normalize_toast_position("TOP LEFT") == "top-left"
    assert _normalize_toast_position("Bottom Right") == "bottom-right"
    assert _normalize_toast_position("MIDDLE center") == "middle-center"


def test_normalize_position_default():
    """Default handling (None or empty)"""
    assert _normalize_toast_position(None) == "bottom-right"
    assert _normalize_toast_position("") == "bottom-right"


def test_normalize_position_all_valid_combinations():
    """All 9 valid position combinations"""
    assert _normalize_toast_position("top left") == "top-left"
    assert _normalize_toast_position("top center") == "top-center"
    assert _normalize_toast_position("top right") == "top-right"
    assert _normalize_toast_position("middle left") == "middle-left"
    assert _normalize_toast_position("middle center") == "middle-center"
    assert _normalize_toast_position("middle right") == "middle-right"
    assert _normalize_toast_position("bottom left") == "bottom-left"
    assert _normalize_toast_position("bottom center") == "bottom-center"
    assert _normalize_toast_position("bottom right") == "bottom-right"


def test_normalize_position_extra_whitespace():
    """Extra whitespace handling"""
    assert _normalize_toast_position("  top   left  ") == "top-left"
    assert _normalize_toast_position("bottom  right") == "bottom-right"


def test_normalize_position_errors():
    """Invalid position inputs"""
    # Missing vertical component
    with pytest.raises(ValueError, match="must include a vertical component"):
        _normalize_toast_position("left")

    # Missing horizontal component
    with pytest.raises(ValueError, match="must include a horizontal component"):
        _normalize_toast_position("top")

    # Duplicate vertical components
    with pytest.raises(ValueError, match="multiple vertical components"):
        _normalize_toast_position("top bottom left")

    # Duplicate horizontal components
    with pytest.raises(ValueError, match="multiple horizontal components"):
        _normalize_toast_position("top left right")

    # Invalid component
    with pytest.raises(ValueError, match="Invalid position component"):
        _normalize_toast_position("top invalid")

    with pytest.raises(ValueError, match="Invalid position component"):
        _normalize_toast_position("foo bar")


# ==============================================================================
# Toast constructor tests
# ==============================================================================


def test_toast_defaults():
    """toast() creates Toast object with defaults"""
    t = ui.toast("Test message")

    assert isinstance(t, Toast)
    assert t.id is None  # ID is not generated until as_payload() is called
    assert t.autohide is True
    assert t.duration == 5000
    assert t.closable is True
    assert t.header is None
    assert t.icon is None
    assert t.position == "top-right"
    assert t.type is None


def test_toast_type_validation():
    """toast() accepts valid types"""
    t1 = ui.toast("Test", type="success")
    assert t1.type == "success"

    t2 = ui.toast("Test", type="danger")
    assert t2.type == "danger"

    t3 = ui.toast("Test", type="info")
    assert t3.type == "info"


def test_toast_type_error_alias():
    """toast() type 'error' is aliased to 'danger'"""
    t = ui.toast("Test", type="error")
    assert t.type == "danger"


def test_toast_autohide_disabled():
    """toast() autohide disabled (0, None)"""
    t1 = ui.toast("Test", duration_s=0, closable=False)
    assert t1.autohide is False
    assert t1.closable is False

    t2 = ui.toast("Test", duration_s=None, closable=False)
    assert t2.autohide is False
    assert t2.closable is False

    # closable can also be True when autohide is disabled
    t3 = ui.toast("Test", duration_s=None, closable=True)
    assert t3.autohide is False
    assert t3.closable is True


def test_toast_closable_with_autohide():
    """toast() closable when autohide enabled"""
    t_closable = ui.toast("Test", duration_s=10, closable=True)
    assert t_closable.autohide is True
    assert t_closable.duration == 10000
    assert t_closable.closable is True

    t_not_closable = ui.toast("Test", duration_s=5, closable=False)
    assert t_not_closable.autohide is True
    assert t_not_closable.duration == 5000
    assert t_not_closable.closable is False


def test_toast_position_formats():
    """toast() works with flexible position formats"""
    # Space-separated
    t1 = ui.toast("Test", position="top left")
    assert t1.position == "top-left"

    # Reversed order
    t2 = ui.toast("Test", position="right bottom")
    assert t2.position == "bottom-right"

    # List
    t3 = ui.toast("Test", position=["middle", "center"])
    assert t3.position == "middle-center"


def test_toast_additional_attributes():
    """toast() stores additional attributes"""
    t = ui.toast("Test", data_test="value", class_="extra-class")

    assert t.attribs["data-test"] == "value"
    assert t.attribs["class"] == "extra-class"


def test_toast_stores_icon_argument():
    """toast() stores icon argument"""
    from htmltools import span

    icon_elem = span("★", class_="test-icon")

    t = ui.toast("Test message", icon=icon_elem)

    assert isinstance(t, Toast)
    assert t.icon is not None
    # Verify it's the icon we passed in (check class attribute)
    assert hasattr(t.icon, "attrs")
    assert "test-icon" in str(t.icon)
    assert "★" in str(t.icon)


def test_toast_icon_is_none_by_default():
    """toast() icon is None by default"""
    t = ui.toast("Test message")
    assert t.icon is None


# ==============================================================================
# Toast rendering tests
# ==============================================================================


def test_toast_tagify_generates_id():
    """Toast.tagify() uses None ID if not provided (ID generated in as_payload())"""
    t = ui.toast("Test message", id=None)
    assert t.id is None

    # When tagify() is called directly without an ID, it will use None
    # (The ID generation only happens in as_payload())
    tag = t.tagify()
    html_str = str(tag)
    # Verify an auto-generated ID is present
    assert re.search(r'id="bslib-toast-[0-9a-f]+"', html_str)

    # When tagify() is called with an explicit ID parameter, it should use it
    tag_with_id = t.tagify(id="test-id")
    html_with_id = str(tag_with_id)
    assert 'id="test-id"' in html_with_id


def test_toast_id_generated_in_as_payload():
    """Toast ID is generated only when as_payload() is called, ensuring uniqueness"""
    from unittest.mock import MagicMock

    # Create toasts without IDs - they should store None
    t1 = ui.toast("Message 1")
    t2 = ui.toast("Message 2")

    assert t1.id is None
    assert t2.id is None

    # Create mock session
    mock_session = MagicMock()
    mock_session._process_ui = MagicMock(
        return_value={"html": "<div>test</div>", "deps": []}
    )

    # Generate payloads - IDs should be generated and different
    payload1 = t1.as_payload(mock_session)
    payload2 = t2.as_payload(mock_session)

    assert payload1 is not None
    assert payload2 is not None
    assert payload1["id"].startswith("bslib-toast-")
    assert payload2["id"].startswith("bslib-toast-")
    assert payload1["id"] != payload2["id"]  # Different IDs

    # Original toast objects should still have None as ID
    assert t1.id is None
    assert t2.id is None


def test_toast_with_user_provided_id_stable():
    """Toast with user-provided ID uses that ID consistently"""
    from unittest.mock import MagicMock

    t = ui.toast("Message", id="my-stable-id")
    assert t.id == "my-stable-id"

    # Create mock session
    mock_session = MagicMock()
    mock_session._process_ui = MagicMock(
        return_value={"html": "<div>test</div>", "deps": []}
    )

    # Payload should use the stable ID
    payload = t.as_payload(mock_session)
    assert payload is not None
    assert payload["id"] == "my-stable-id"
    assert t.id == "my-stable-id"  # Should remain unchanged


def test_toast_tagify_accessibility_danger():
    """Toast.tagify() respects accessibility attributes for danger type"""
    t = ui.toast("Error message", type="danger", id="danger-toast")
    tag = t.tagify()
    html = str(tag)

    assert 'role="alert"' in html
    assert 'aria-live="assertive"' in html


def test_toast_tagify_accessibility_other():
    """Toast.tagify() respects accessibility attributes for non-danger types"""
    # Info type gets polite role
    t_info = ui.toast("Info message", type="info", id="info-toast")
    html_info = str(t_info.tagify())
    assert 'role="status"' in html_info
    assert 'aria-live="polite"' in html_info

    # Default (no type) gets polite role
    t_default = ui.toast("Default message", id="default-toast")
    html_default = str(t_default.tagify())
    assert 'role="status"' in html_default
    assert 'aria-live="polite"' in html_default


def test_toast_tagify_type_classes():
    """Toast type is reflected in rendered HTML classes"""
    t_success = ui.toast("Test", type="success")
    html_success = str(t_success.tagify())
    assert "text-bg-success" in html_success

    t_danger = ui.toast("Test", type="danger")
    html_danger = str(t_danger.tagify())
    assert "text-bg-danger" in html_danger


def test_toast_tagify_close_button_placement():
    """Toast.tagify() includes close button appropriately"""
    # With header, closable
    t_header = ui.toast("Message", header="Title", closable=True, id="header-toast")
    html_header = str(t_header.tagify())
    assert "btn-close" in html_header
    assert "toast-header" in html_header

    # Without header, closable
    t_no_header = ui.toast("Message", closable=True, id="no-header-toast")
    html_no_header = str(t_no_header.tagify())
    assert "btn-close" in html_no_header

    # Non-closable with autohide
    t_non_closable = ui.toast(
        "Message", closable=False, duration_s=5, id="non-closable-toast"
    )
    html_non_closable = str(t_non_closable.tagify())
    # Should not have close button
    assert "btn-close" not in html_non_closable


def test_toast_tagify_autohide_attribute():
    """Toast.tagify() sets data-bs-autohide attribute"""
    t_autohide = ui.toast("Test", duration_s=5)
    html_autohide = str(t_autohide.tagify())
    assert 'data-bs-autohide="true"' in html_autohide

    t_no_autohide = ui.toast("Test", duration_s=None)
    html_no_autohide = str(t_no_autohide.tagify())
    assert 'data-bs-autohide="false"' in html_no_autohide


def test_toast_icon_renders_in_body_without_header(snapshot: Any):
    """toast() icon renders in body without header"""
    from htmltools import span

    icon_elem = span("★", class_="my-icon")
    t = ui.toast("You have new messages", icon=icon_elem, id="icon-toast")

    tag = t.tagify()
    html = str(tag)

    # Icon should be in toast-body with special wrapper
    assert "toast-body" in html
    assert "toast-body-icon" in html
    assert "my-icon" in html
    assert "★" in html
    assert "toast-body-content" in html
    assert html == snapshot


def test_toast_icon_renders_in_body_with_header(snapshot: Any):
    """toast() icon renders in body with header"""
    from htmltools import span

    icon_elem = span("★", class_="header-icon")
    t = ui.toast(
        "Message content",
        header="New Mail",
        icon=icon_elem,
        id="icon-header-toast",
    )

    tag = t.tagify()
    html = str(tag)

    # Icon should still be in body when header is present
    assert "toast-body" in html
    assert "toast-body-icon" in html
    assert "header-icon" in html
    assert "★" in html
    assert html == snapshot


def test_toast_icon_works_with_closable_button_in_body(snapshot: Any):
    """toast() icon works with closable button in body"""
    from htmltools import span

    icon_elem = span("★", class_="alert-icon")
    t = ui.toast(
        "Warning message",
        icon=icon_elem,
        closable=True,
        id="icon-closable-toast",
    )

    tag = t.tagify()
    html = str(tag)

    # Should have both icon and close button in body
    assert "toast-body" in html
    assert "toast-body-icon" in html
    assert "alert-icon" in html
    assert "★" in html
    assert "btn-close" in html
    assert html == snapshot


def test_toast_without_icon_or_close_button_has_simple_body():
    """toast() without icon or close button has simple body"""
    t = ui.toast(
        "Simple message",
        header="Header",
        closable=False,
        id="simple-body-toast",
    )

    tag = t.tagify()
    html = str(tag)

    # Should have simple toast-body (no extra wrapper elements)
    assert "toast-body" in html
    assert "toast-body-icon" not in html
    assert "toast-body-content" not in html


# ==============================================================================
# ToastHeader tests
# ==============================================================================


def test_toast_header_simple():
    """toast_header() creates simple header with just title"""
    h = ui.toast_header("My Title")

    assert isinstance(h, ToastHeader)
    assert h.title == "My Title"
    assert h.icon is None
    assert h.status is None


def test_toast_header_with_status():
    """toast_header() with status text"""
    h = ui.toast_header("Success", status="11 mins ago")

    assert isinstance(h, ToastHeader)
    assert h.title == "Success"
    assert h.status == "11 mins ago"


def test_toast_header_with_icon():
    """toast_header() works with icons"""
    from htmltools import span

    icon = span(class_="test-icon")
    h = ui.toast_header("Title", icon=icon)

    assert isinstance(h, ToastHeader)
    assert h.title == "Title"
    assert h.icon is not None


def test_toast_header_tagify():
    """ToastHeader.tagify() creates proper HTML structure"""
    h = ui.toast_header("My Title", status="just now")
    tag = h.tagify()
    html = str(tag)

    assert "toast-header" in html
    assert "My Title" in html
    assert "just now" in html


def test_toast_header_icon_renders_in_header(snapshot: Any):
    """toast_header() icon renders in header"""
    from htmltools import span

    icon_elem = span("★", class_="header-test-icon")
    h = ui.toast_header("Notification", icon=icon_elem, status="now")

    t = ui.toast("Body content", header=h, id="header-icon-toast")
    tag = t.tagify()
    html = str(tag)

    # Icon should be in toast-header with wrapper
    assert "toast-header" in html
    assert "toast-header-icon" in html
    assert "header-test-icon" in html
    assert "★" in html
    assert html == snapshot


def test_toast_header_icon_with_status_and_title(snapshot: Any):
    """toast_header() icon with status and title"""
    from htmltools import span

    icon_elem = span("✓", class_="success-icon")
    h = ui.toast_header("Success", icon=icon_elem, status="just now")

    t = ui.toast("Operation completed", header=h, id="full-header-toast")
    tag = t.tagify()
    html = str(tag)

    # Should have all three elements: icon, title, status
    assert "toast-header-icon" in html
    assert "success-icon" in html
    assert "✓" in html
    assert "Success" in html
    assert "just now" in html
    assert html == snapshot


# ==============================================================================
# Toast header integration tests
# ==============================================================================


def test_toast_with_string_header():
    """toast() with character header"""
    t = ui.toast("Body", header="Simple Header")
    tag = t.tagify()
    html = str(tag)

    assert "toast-header" in html
    assert "Simple Header" in html


def test_toast_with_toast_header_object():
    """toast() with toast_header() object"""
    t = ui.toast("Body", header=ui.toast_header("Title", status="just now"))
    tag = t.tagify()
    html = str(tag)

    assert "toast-header" in html
    assert "Title" in html
    assert "just now" in html


def test_toast_with_custom_tag_header(snapshot: Any):
    """toast() with custom tag as header"""
    from htmltools import div

    t = ui.toast(
        "Body",
        header=div("My Header", class_="custom-header"),
        id="custom-header-toast",
    )

    tag = t.tagify()
    html = str(tag)

    # The custom header should be rendered
    assert "custom-header" in html
    assert "My Header" in html
    assert html == snapshot


# ==============================================================================
# Integration tests (basic structure checks)
# ==============================================================================


def test_toast_position_stored_correctly():
    """toast() position is stored correctly"""
    t1 = ui.toast("Test", position="top-left")
    assert t1.position == "top-left"

    t2 = ui.toast("Test", position="middle-center")
    assert t2.position == "middle-center"

    t3 = ui.toast("Test", position="bottom-right")
    assert t3.position == "bottom-right"


def test_toast_body_and_header_structure():
    """Toast renders with proper body and header structure"""
    t = ui.toast("Test body", header="Test header", id="test-toast", type="success")

    tag = t.tagify()
    html = str(tag)

    # Check basic structure
    assert 'id="test-toast"' in html
    assert 'class="toast' in html
    assert "text-bg-success" in html
    assert "toast-header" in html
    assert "toast-body" in html
    assert "Test body" in html
    assert "Test header" in html


def test_toast_with_both_header_icon_and_body_icon(snapshot: Any):
    """toast() with both header icon and body icon"""
    from htmltools import span

    # Both header and body can have their own icons
    header_icon = span("H", class_="h-icon")
    body_icon = span("B", class_="b-icon")

    t = ui.toast(
        "Message content",
        header=ui.toast_header("Title", icon=header_icon),
        icon=body_icon,
        id="dual-icon-toast",
    )

    tag = t.tagify()
    html = str(tag)

    # Both icons should be present in different locations
    assert "toast-header-icon" in html
    assert "h-icon" in html
    assert "toast-body-icon" in html
    assert "b-icon" in html
    assert html == snapshot
