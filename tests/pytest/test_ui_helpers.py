"""Tests for notification and download helper functions."""

from shiny.ui import (
    download_link,
    download_button,
    panel_well,
    panel_conditional,
    panel_title,
    panel_fixed,
    panel_absolute,
    help_text,
)
from htmltools import tags


class TestDownloadUI:
    """Tests for download UI components."""

    def test_download_link(self):
        """Test creating a download link."""
        link = download_link("my_download", "Download Data")
        html = str(link)

        assert 'id="my_download"' in html
        assert "Download Data" in html
        assert "download" in html.lower() or "shiny-download-link" in html

    def test_download_button(self):
        """Test creating a download button."""
        btn = download_button("my_download", "Download")
        html = str(btn)

        assert 'id="my_download"' in html
        assert "Download" in html

    def test_download_button_with_class(self):
        """Test download button with custom class."""
        btn = download_button("my_download", "Get File", class_="btn-success")
        html = str(btn)

        assert "btn-success" in html


class TestPanels:
    """Tests for panel UI components."""

    def test_panel_well(self):
        """Test creating a well panel."""
        well = panel_well("Well content")
        html = str(well)

        assert "well" in html
        assert "Well content" in html

    def test_panel_conditional(self):
        """Test creating a conditional panel."""
        panel = panel_conditional("input.show_panel", "This content is conditional")
        html = str(panel)

        assert "conditional" in html.lower() or "shiny-panel-conditional" in html
        assert "input.show_panel" in html or "data-display-if" in html

    def test_panel_title(self):
        """Test creating a title panel."""
        title = panel_title("My Application")
        html = str(title)

        assert "My Application" in html

    def test_panel_title_with_window_title(self):
        """Test title panel with explicit window title."""
        title = panel_title("App Title", "Browser Title")
        html = str(title)

        assert "App Title" in html


class TestPanelFixed:
    """Tests for panel_fixed function."""

    def test_basic_panel_fixed(self):
        """Test creating a basic fixed panel."""
        panel = panel_fixed("Fixed content")
        html = str(panel)

        assert "Fixed content" in html
        assert "position" in html.lower()


class TestPanelAbsolute:
    """Tests for panel_absolute function."""

    def test_basic_panel_absolute(self):
        """Test creating a basic absolute panel."""
        panel = panel_absolute("Absolute content")
        html = str(panel)

        assert "Absolute content" in html
        assert "absolute" in html.lower()

    def test_panel_absolute_with_position(self):
        """Test absolute panel with position."""
        panel = panel_absolute("Content", top="10px", left="20px")
        html = str(panel)

        assert "Content" in html


class TestHelpText:
    """Tests for help_text function."""

    def test_basic_help_text(self):
        """Test creating basic help text."""
        help_elem = help_text("This is helpful information.")
        html = str(help_elem)

        assert "This is helpful information." in html
        assert "help" in html.lower()

    def test_help_text_with_multiple_children(self):
        """Test help text with multiple children."""
        help_elem = help_text("Line 1", tags.br(), "Line 2")
        html = str(help_elem)

        assert "Line 1" in html
        assert "Line 2" in html
