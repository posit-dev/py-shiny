"""Tests for shiny.ui._toast module."""

from htmltools import Tag, tags

from shiny.ui._toast import Toast, ToastHeader, toast, toast_header


class TestToast:
    """Tests for toast function."""

    def test_toast_basic(self) -> None:
        """Test basic toast creation."""
        result = toast("Hello world")
        assert isinstance(result, Toast)

    def test_toast_with_header(self) -> None:
        """Test toast with header string."""
        result = toast("Content", header="My Toast")
        assert result.header is not None
        assert isinstance(result.header, ToastHeader)

    def test_toast_with_header_object(self) -> None:
        """Test toast with ToastHeader object."""
        hdr = toast_header("Custom Header")
        result = toast("Content", header=hdr)
        assert result.header is hdr

    def test_toast_tagify(self) -> None:
        """Test toast tagify produces Tag."""
        result = toast("Hello")
        tag = result.tagify()
        assert isinstance(tag, Tag)
        html = str(tag)
        assert "Hello" in html
        assert "toast" in html

    def test_toast_with_type(self) -> None:
        """Test toast with type parameter."""
        result = toast("Success!", type="success")
        assert result.type == "success"
        html = str(result.tagify())
        assert "text-bg-success" in html

    def test_toast_with_danger_type(self) -> None:
        """Test toast with danger type."""
        result = toast("Error!", type="danger")
        assert result.type == "danger"
        html = str(result.tagify())
        assert "text-bg-danger" in html
        # Danger should have alert role
        assert 'role="alert"' in html

    def test_toast_with_error_type_normalizes_to_danger(self) -> None:
        """Test toast with error type normalizes to danger."""
        result = toast("Error!", type="error")
        assert result.type == "danger"

    def test_toast_with_duration(self) -> None:
        """Test toast with duration_s parameter."""
        result = toast("Auto hide", duration_s=10)
        assert result.duration == 10000  # Converted to milliseconds
        assert result.autohide is True

    def test_toast_no_autohide(self) -> None:
        """Test toast with no auto-hide."""
        result = toast("Persistent", duration_s=None)
        assert result.autohide is False

    def test_toast_with_position(self) -> None:
        """Test toast with position parameter."""
        result = toast("Hello", position="bottom-left")
        assert result.position == "bottom-left"

    def test_toast_with_position_list(self) -> None:
        """Test toast with position as list."""
        result = toast("Hello", position=["top", "left"])
        assert result.position == "top-left"

    def test_toast_closable(self) -> None:
        """Test toast with closable parameter."""
        result = toast("Hello", closable=True)
        assert result.closable is True
        html = str(result.tagify())
        assert "btn-close" in html

    def test_toast_not_closable(self) -> None:
        """Test toast with closable=False."""
        result = toast("Hello", closable=False)
        assert result.closable is False

    def test_toast_with_icon(self) -> None:
        """Test toast with icon parameter."""
        icon = tags.span("icon")
        result = toast("Hello", icon=icon)
        html = str(result.tagify())
        assert "toast-body-icon" in html

    def test_toast_with_id(self) -> None:
        """Test toast with custom id."""
        result = toast("Hello", id="my-toast")
        assert result.id == "my-toast"
        html = str(result.tagify())
        assert 'id="my-toast"' in html


class TestToastHeader:
    """Tests for toast_header function."""

    def test_toast_header_basic(self) -> None:
        """Test basic toast_header creation."""
        result = toast_header("My Title")
        assert isinstance(result, ToastHeader)
        assert result.title == "My Title"

    def test_toast_header_with_icon(self) -> None:
        """Test toast_header with icon."""
        icon = tags.span("icon")
        result = toast_header("Title", icon=icon)
        assert result.icon is icon

    def test_toast_header_with_status(self) -> None:
        """Test toast_header with status."""
        result = toast_header("Title", status="just now")
        assert result.status == "just now"

    def test_toast_header_tagify(self) -> None:
        """Test toast_header tagify produces Tag."""
        result = toast_header("Title")
        tag = result.tagify()
        assert isinstance(tag, Tag)
        html = str(tag)
        assert "toast-header" in html
        assert "Title" in html

    def test_toast_header_with_close_button(self) -> None:
        """Test toast_header tagify with close button."""
        result = toast_header("Title")
        close_btn = tags.button(class_="btn-close")
        tag = result.tagify(close_button=close_btn)
        html = str(tag)
        assert "btn-close" in html

    def test_toast_header_tagify_with_status(self) -> None:
        """Test toast_header tagify includes status."""
        result = toast_header("Title", status="5 mins ago")
        tag = result.tagify()
        html = str(tag)
        assert "5 mins ago" in html
        assert "text-muted" in html


class TestToastIntegration:
    """Integration tests for toast functionality."""

    def test_toast_with_header_and_body(self) -> None:
        """Test toast with both header and body."""
        result = toast(
            "This is the body content",
            header=toast_header("Notification", status="now"),
            type="info",
        )
        html = str(result.tagify())
        assert "This is the body content" in html
        assert "Notification" in html
        assert "now" in html
        assert "text-bg-info" in html

    def test_toast_multiple_body_children(self) -> None:
        """Test toast with multiple body children."""
        result = toast("First", tags.span("Second"), tags.strong("Third"))
        html = str(result.tagify())
        assert "First" in html
        assert "Second" in html
        assert "Third" in html

    def test_toast_positions(self) -> None:
        """Test various toast positions."""
        positions = [
            "top-left",
            "top-center",
            "top-right",
            "middle-left",
            "middle-center",
            "middle-right",
            "bottom-left",
            "bottom-center",
            "bottom-right",
        ]
        for pos in positions:
            result = toast("Hello", position=pos)
            assert result.position == pos
