"""Tests for the SidebarOpen class."""

import pytest

from shiny.ui._sidebar import SidebarOpen


class TestSidebarOpen:
    """Tests for the SidebarOpen class."""

    def test_sidebar_open_default(self):
        """Test default values for SidebarOpen."""
        sidebar_open = SidebarOpen()

        assert sidebar_open.desktop == "open"
        assert sidebar_open.mobile == "closed"

    def test_sidebar_open_custom_values(self):
        """Test custom values for SidebarOpen."""
        sidebar_open = SidebarOpen(desktop="closed", mobile="open")

        assert sidebar_open.desktop == "closed"
        assert sidebar_open.mobile == "open"

    def test_sidebar_open_always(self):
        """Test SidebarOpen with always values."""
        sidebar_open = SidebarOpen(desktop="always", mobile="always")

        assert sidebar_open.desktop == "always"
        assert sidebar_open.mobile == "always"

    def test_sidebar_open_always_above(self):
        """Test SidebarOpen with always-above mobile value."""
        sidebar_open = SidebarOpen(desktop="open", mobile="always-above")

        assert sidebar_open.mobile == "always-above"

    def test_sidebar_open_invalid_desktop(self):
        """Test that invalid desktop value raises error."""
        with pytest.raises(ValueError, match="desktop"):
            SidebarOpen(desktop="invalid")  # type: ignore[arg-type]

    def test_sidebar_open_invalid_mobile(self):
        """Test that invalid mobile value raises error."""
        with pytest.raises(ValueError, match="mobile"):
            SidebarOpen(mobile="invalid")  # type: ignore[arg-type]


class TestSidebarOpenIsAlwaysOpen:
    """Tests for the _is_always_open method."""

    def test_is_always_open_both(self):
        """Test _is_always_open with both always."""
        sidebar_open = SidebarOpen(desktop="always", mobile="always")

        assert sidebar_open._is_always_open("both") is True
        assert sidebar_open._is_always_open("desktop") is True
        assert sidebar_open._is_always_open("mobile") is True

    def test_is_always_open_desktop_only(self):
        """Test _is_always_open with desktop always."""
        sidebar_open = SidebarOpen(desktop="always", mobile="closed")

        assert sidebar_open._is_always_open("both") is False
        assert sidebar_open._is_always_open("desktop") is True
        assert sidebar_open._is_always_open("mobile") is False

    def test_is_always_open_mobile_only(self):
        """Test _is_always_open with mobile always."""
        sidebar_open = SidebarOpen(desktop="open", mobile="always")

        assert sidebar_open._is_always_open("both") is False
        assert sidebar_open._is_always_open("desktop") is False
        assert sidebar_open._is_always_open("mobile") is True

    def test_is_always_open_mobile_always_above(self):
        """Test _is_always_open with mobile always-above."""
        sidebar_open = SidebarOpen(desktop="open", mobile="always-above")

        assert sidebar_open._is_always_open("mobile") is True

    def test_is_always_open_none(self):
        """Test _is_always_open with neither always."""
        sidebar_open = SidebarOpen(desktop="open", mobile="closed")

        assert sidebar_open._is_always_open("both") is False
        assert sidebar_open._is_always_open("desktop") is False
        assert sidebar_open._is_always_open("mobile") is False


class TestSidebarOpenFromString:
    """Tests for the _from_string class method."""

    def test_from_string_open(self):
        """Test _from_string with 'open'."""
        result = SidebarOpen._from_string("open")

        assert result.desktop == "open"
        assert result.mobile == "open"

    def test_from_string_closed(self):
        """Test _from_string with 'closed'."""
        result = SidebarOpen._from_string("closed")

        assert result.desktop == "closed"
        assert result.mobile == "closed"

    def test_from_string_always(self):
        """Test _from_string with 'always'."""
        result = SidebarOpen._from_string("always")

        assert result.desktop == "always"
        assert result.mobile == "always"

    def test_from_string_desktop(self):
        """Test _from_string with 'desktop' (special case)."""
        result = SidebarOpen._from_string("desktop")

        assert result.desktop == "open"
        assert result.mobile == "closed"

    def test_from_string_invalid(self):
        """Test _from_string with invalid value."""
        with pytest.raises(ValueError):
            SidebarOpen._from_string("invalid")

    def test_from_string_empty(self):
        """Test _from_string with empty string."""
        with pytest.raises(ValueError):
            SidebarOpen._from_string("")

    def test_from_string_not_string(self):
        """Test _from_string with non-string value."""
        with pytest.raises(ValueError):
            SidebarOpen._from_string(123)  # type: ignore[arg-type]


class TestSidebarOpenAsOpen:
    """Tests for the _as_open class method."""

    def test_as_open_with_string(self):
        """Test _as_open with string value."""
        result = SidebarOpen._as_open("open")

        assert result.desktop == "open"
        assert result.mobile == "open"

    def test_as_open_with_dict(self):
        """Test _as_open with dictionary."""
        result = SidebarOpen._as_open({"desktop": "closed", "mobile": "open"})

        assert result.desktop == "closed"
        assert result.mobile == "open"

    def test_as_open_with_desktop_string(self):
        """Test _as_open with 'desktop' string."""
        result = SidebarOpen._as_open("desktop")

        assert result.desktop == "open"
        assert result.mobile == "closed"

    def test_as_open_invalid_type(self):
        """Test _as_open with invalid type raises error."""
        with pytest.raises(ValueError):
            SidebarOpen._as_open(123)  # type: ignore[arg-type]
