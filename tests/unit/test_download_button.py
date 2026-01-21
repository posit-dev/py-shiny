"""Unit tests for shiny.ui._download_button module."""

from __future__ import annotations

from htmltools import Tag, tags

from shiny.ui import download_button, download_link


class TestDownloadButton:
    """Tests for download_button function."""

    def test_basic_download_button(self) -> None:
        """Test basic download_button with required parameters."""
        result = download_button("download_id", "Download")
        html = str(result)

        assert 'id="download_id"' in html
        assert "Download" in html
        assert "<a" in html  # Should be an anchor element

    def test_download_button_returns_tag(self) -> None:
        """Test that download_button returns a Tag."""
        result = download_button("download_id", "Download")
        assert isinstance(result, Tag)

    def test_download_button_btn_class(self) -> None:
        """Test download_button has btn class."""
        result = download_button("download_id", "Download")
        html = str(result)

        assert "btn" in html
        assert "btn-default" in html

    def test_download_button_shiny_download_link_class(self) -> None:
        """Test download_button has shiny-download-link class."""
        result = download_button("download_id", "Download")
        html = str(result)

        assert "shiny-download-link" in html

    def test_download_button_with_icon(self) -> None:
        """Test download_button with icon parameter."""
        icon = tags.i(class_="fa fa-download")
        result = download_button("download_id", "Download", icon=icon)
        html = str(result)

        assert "fa-download" in html

    def test_download_button_with_width(self) -> None:
        """Test download_button with width parameter."""
        result = download_button("download_id", "Download", width="200px")
        html = str(result)

        assert "width:200px" in html

    def test_download_button_target_blank(self) -> None:
        """Test download_button has target='_blank'."""
        result = download_button("download_id", "Download")
        html = str(result)

        assert 'target="_blank"' in html

    def test_download_button_disabled_by_default(self) -> None:
        """Test download_button is disabled by default."""
        result = download_button("download_id", "Download")
        html = str(result)

        assert "disabled" in html
        assert 'aria-disabled="true"' in html

    def test_download_button_tabindex(self) -> None:
        """Test download_button has tabindex='-1' when disabled."""
        result = download_button("download_id", "Download")
        html = str(result)

        assert 'tabindex="-1"' in html

    def test_download_button_custom_kwargs(self) -> None:
        """Test download_button with custom kwargs."""
        result = download_button(
            "download_id", "Download", class_="custom-class", data_custom="value"
        )
        html = str(result)

        assert "custom-class" in html
        assert 'data-custom="value"' in html

    def test_download_button_html_label(self) -> None:
        """Test download_button with HTML label."""
        label = tags.strong("Bold Download")
        result = download_button("download_id", label)
        html = str(result)

        assert "<strong>Bold Download</strong>" in html


class TestDownloadLink:
    """Tests for download_link function."""

    def test_basic_download_link(self) -> None:
        """Test basic download_link with required parameters."""
        result = download_link("link_id", "Download Link")
        html = str(result)

        assert 'id="link_id"' in html
        assert "Download Link" in html
        assert "<a" in html

    def test_download_link_returns_tag(self) -> None:
        """Test that download_link returns a Tag."""
        result = download_link("link_id", "Link")
        assert isinstance(result, Tag)

    def test_download_link_shiny_download_link_class(self) -> None:
        """Test download_link has shiny-download-link class."""
        result = download_link("link_id", "Link")
        html = str(result)

        assert "shiny-download-link" in html

    def test_download_link_with_icon(self) -> None:
        """Test download_link with icon parameter."""
        icon = tags.i(class_="fa fa-file")
        result = download_link("link_id", "Link", icon=icon)
        html = str(result)

        assert "fa-file" in html

    def test_download_link_with_width(self) -> None:
        """Test download_link with width parameter."""
        result = download_link("link_id", "Link", width="150px")
        html = str(result)

        assert "width:150px" in html

    def test_download_link_target_blank(self) -> None:
        """Test download_link has target='_blank'."""
        result = download_link("link_id", "Link")
        html = str(result)

        assert 'target="_blank"' in html

    def test_download_link_disabled_by_default(self) -> None:
        """Test download_link is disabled by default."""
        result = download_link("link_id", "Link")
        html = str(result)

        assert "disabled" in html
        assert 'aria-disabled="true"' in html

    def test_download_link_custom_kwargs(self) -> None:
        """Test download_link with custom kwargs."""
        result = download_link("link_id", "Link", data_info="test")
        html = str(result)

        assert 'data-info="test"' in html

    def test_download_link_html_label(self) -> None:
        """Test download_link with HTML label."""
        label = tags.em("Italic Link")
        result = download_link("link_id", label)
        html = str(result)

        assert "<em>Italic Link</em>" in html
