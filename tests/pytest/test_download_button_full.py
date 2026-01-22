"""Tests for shiny/ui/_download_button.py module."""

from shiny.ui._download_button import download_button, download_link


class TestDownloadButton:
    """Tests for download_button function."""

    def test_download_button_is_callable(self):
        """Test download_button is callable."""
        assert callable(download_button)

    def test_download_button_returns_tag(self):
        """Test download_button returns a Tag."""
        from htmltools import Tag

        result = download_button("my_download", "Download")
        assert isinstance(result, Tag)

    def test_download_button_with_class(self):
        """Test download_button with class_ parameter."""
        from htmltools import Tag

        result = download_button("my_download", "Download", class_="btn-primary")
        assert isinstance(result, Tag)


class TestDownloadLink:
    """Tests for download_link function."""

    def test_download_link_is_callable(self):
        """Test download_link is callable."""
        assert callable(download_link)

    def test_download_link_returns_tag(self):
        """Test download_link returns a Tag."""
        from htmltools import Tag

        result = download_link("my_download", "Download")
        assert isinstance(result, Tag)


class TestDownloadExported:
    """Tests for download functions export."""

    def test_download_button_in_ui(self):
        """Test download_button is in ui module."""
        from shiny import ui

        assert hasattr(ui, "download_button")

    def test_download_link_in_ui(self):
        """Test download_link is in ui module."""
        from shiny import ui

        assert hasattr(ui, "download_link")
