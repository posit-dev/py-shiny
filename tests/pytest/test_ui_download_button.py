"""Tests for shiny/ui/_download_button.py"""

from __future__ import annotations

from htmltools import Tag

from shiny.ui._download_button import download_button, download_link


class TestDownloadButton:
    """Tests for download_button function."""

    def test_download_button_basic(self) -> None:
        """Test basic download button creation."""
        result = download_button("dl", "Download")
        assert isinstance(result, Tag)
        html = str(result)
        assert "dl" in html
        assert "Download" in html
        assert "shiny-download-link" in html

    def test_download_button_with_icon(self) -> None:
        """Test download button with icon."""
        result = download_button("dl", "Download", icon="↓")
        html = str(result)
        assert "↓" in html

    def test_download_button_with_width(self) -> None:
        """Test download button with width."""
        result = download_button("dl", "Download", width="200px")
        html = str(result)
        assert "200px" in html

    def test_download_button_with_kwargs(self) -> None:
        """Test download button with custom attributes."""
        result = download_button("dl", "Download", class_="custom-btn")
        html = str(result)
        assert "custom-btn" in html

    def test_download_button_has_btn_class(self) -> None:
        """Test download button has btn-default class."""
        result = download_button("dl", "Download")
        html = str(result)
        assert "btn-default" in html


class TestDownloadLink:
    """Tests for download_link function."""

    def test_download_link_basic(self) -> None:
        """Test basic download link creation."""
        result = download_link("dl", "Download")
        assert isinstance(result, Tag)
        html = str(result)
        assert "dl" in html
        assert "Download" in html
        assert "shiny-download-link" in html

    def test_download_link_with_icon(self) -> None:
        """Test download link with icon."""
        result = download_link("dl", "Download", icon="↓")
        html = str(result)
        assert "↓" in html

    def test_download_link_with_width(self) -> None:
        """Test download link with width."""
        result = download_link("dl", "Download", width="200px")
        html = str(result)
        assert "200px" in html

    def test_download_link_no_btn_class(self) -> None:
        """Test download link does not have btn-default class."""
        result = download_link("dl", "Download")
        html = str(result)
        assert "btn-default" not in html
