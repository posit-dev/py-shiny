"""Tests for shiny.ui._download_button module."""

from htmltools import Tag

from shiny.ui._download_button import download_button, download_link


class TestDownloadButton:
    """Tests for download_button function."""

    def test_download_button_basic(self) -> None:
        """Test basic download_button creation."""
        result = download_button("my_download", "Download")
        assert isinstance(result, Tag)

    def test_download_button_has_id(self) -> None:
        """Test download_button has correct id."""
        result = download_button("download_id", "Label")
        html = str(result)
        assert "download_id" in html

    def test_download_button_with_label(self) -> None:
        """Test download_button with label."""
        result = download_button("download", "Download Data")
        html = str(result)
        assert "Download Data" in html

    def test_download_button_is_anchor(self) -> None:
        """Test download_button returns anchor tag."""
        result = download_button("download", "Label")
        assert result.name == "a"

    def test_download_button_has_download_attribute(self) -> None:
        """Test download_button has download attribute."""
        result = download_button("download", "Label")
        html = str(result)
        assert "download" in html

    def test_download_button_with_class(self) -> None:
        """Test download_button with class_ parameter."""
        result = download_button("download", "Label", class_="btn-success")
        html = str(result)
        assert "btn-success" in html

    def test_download_button_btn_class(self) -> None:
        """Test download_button has btn class."""
        result = download_button("download", "Label")
        html = str(result)
        assert "btn" in html


class TestDownloadLink:
    """Tests for download_link function."""

    def test_download_link_basic(self) -> None:
        """Test basic download_link creation."""
        result = download_link("my_link", "Download")
        assert isinstance(result, Tag)

    def test_download_link_has_id(self) -> None:
        """Test download_link has correct id."""
        result = download_link("link_id", "Label")
        html = str(result)
        assert "link_id" in html

    def test_download_link_with_label(self) -> None:
        """Test download_link with label."""
        result = download_link("link", "Download File")
        html = str(result)
        assert "Download File" in html

    def test_download_link_is_anchor(self) -> None:
        """Test download_link returns anchor tag."""
        result = download_link("link", "Label")
        assert result.name == "a"

    def test_download_link_has_download_attribute(self) -> None:
        """Test download_link has download attribute."""
        result = download_link("link", "Label")
        html = str(result)
        assert "download" in html
