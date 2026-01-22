"""Tests for shiny.ui._download_button module."""

from shiny.ui import download_button, download_link


class TestDownloadButton:
    """Tests for download_button function."""

    def test_download_button_basic(self):
        """Test basic download_button creation."""
        btn = download_button("download_id", "Download")
        assert btn.name == "a"
        html = str(btn)
        assert "download_id" in html
        assert "Download" in html

    def test_download_button_with_icon(self):
        """Test download_button with icon."""
        btn = download_button("download_id", "Download", icon="📥")
        html = str(btn)
        assert "📥" in html

    def test_download_button_with_width(self):
        """Test download_button with width."""
        btn = download_button("download_id", "Download", width="200px")
        html = str(btn)
        assert "200px" in html

    def test_download_button_class(self):
        """Test download_button has correct CSS class."""
        btn = download_button("download_id", "Download")
        html = str(btn)
        assert "shiny-download-link" in html
        assert "btn" in html

    def test_download_button_disabled(self):
        """Test download_button is initially disabled."""
        btn = download_button("download_id", "Download")
        html = str(btn)
        assert "disabled" in html
        assert 'aria-disabled="true"' in html

    def test_download_button_with_kwargs(self):
        """Test download_button with additional attributes."""
        btn = download_button(
            "download_id", "Download", class_="custom-class", data_value="test"
        )
        html = str(btn)
        assert "custom-class" in html
        assert "data-value" in html


class TestDownloadLink:
    """Tests for download_link function."""

    def test_download_link_basic(self):
        """Test basic download_link creation."""
        link = download_link("download_id", "Download")
        assert link.name == "a"
        html = str(link)
        assert "download_id" in html
        assert "Download" in html

    def test_download_link_with_icon(self):
        """Test download_link with icon."""
        link = download_link("download_id", "Download", icon="📥")
        html = str(link)
        assert "📥" in html

    def test_download_link_with_width(self):
        """Test download_link with width."""
        link = download_link("download_id", "Download", width="200px")
        html = str(link)
        assert "200px" in html

    def test_download_link_class(self):
        """Test download_link has correct CSS class."""
        link = download_link("download_id", "Download")
        html = str(link)
        assert "shiny-download-link" in html
        # download_link should not have btn class
        classes = link.attrs.get("class", "")
        assert "btn btn-default" not in classes

    def test_download_link_disabled(self):
        """Test download_link is initially disabled."""
        link = download_link("download_id", "Download")
        html = str(link)
        assert "disabled" in html
        assert 'aria-disabled="true"' in html

    def test_download_link_with_kwargs(self):
        """Test download_link with additional attributes."""
        link = download_link(
            "download_id", "Download", class_="custom-class", data_value="test"
        )
        html = str(link)
        assert "custom-class" in html
        assert "data-value" in html
