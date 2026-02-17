"""Comprehensive tests for shiny.ui._download_button module."""

from htmltools import Tag


class TestDownloadButton:
    """Tests for download_button function."""

    def test_download_button_basic(self):
        """download_button should create a link element."""
        from shiny.ui import download_button

        result = download_button("dl", "Download")
        assert isinstance(result, Tag)
        assert result.name == "a"
        assert result.attrs.get("id") == "dl"

    def test_download_button_with_label(self):
        """download_button should display label."""
        from shiny.ui import download_button

        result = download_button("dl", "Download File")
        html_str = str(result)
        assert "Download File" in html_str

    def test_download_button_with_icon(self):
        """download_button should include icon."""
        from shiny.ui import download_button

        result = download_button("dl", "Download", icon="📥")
        html_str = str(result)
        assert "📥" in html_str

    def test_download_button_has_default_class(self):
        """download_button should have btn and shiny-download-link classes."""
        from shiny.ui import download_button

        result = download_button("dl", "Download")
        assert "btn" in result.attrs.get("class", "")
        assert "btn-default" in result.attrs.get("class", "")
        assert "shiny-download-link" in result.attrs.get("class", "")

    def test_download_button_is_disabled_initially(self):
        """download_button should be disabled initially."""
        from shiny.ui import download_button

        result = download_button("dl", "Download")
        assert "disabled" in result.attrs.get("class", "")
        assert result.attrs.get("aria-disabled") == "true"
        assert result.attrs.get("tabindex") == "-1"

    def test_download_button_has_empty_href(self):
        """download_button should have empty href initially."""
        from shiny.ui import download_button

        result = download_button("dl", "Download")
        assert result.attrs.get("href") == ""

    def test_download_button_has_target_blank(self):
        """download_button should open in new tab."""
        from shiny.ui import download_button

        result = download_button("dl", "Download")
        assert result.attrs.get("target") == "_blank"

    def test_download_button_with_width(self):
        """download_button should accept width parameter."""
        from shiny.ui import download_button

        result = download_button("dl", "Download", width="150px")
        html_str = str(result)
        assert "150px" in html_str

    def test_download_button_with_kwargs(self):
        """download_button should accept additional attributes."""
        from shiny.ui import download_button

        result = download_button("dl", "Download", data_test="value", custom="attr")
        assert result.attrs.get("data-test") == "value"
        assert result.attrs.get("custom") == "attr"


class TestDownloadLink:
    """Tests for download_link function."""

    def test_download_link_basic(self):
        """download_link should create a link element."""
        from shiny.ui import download_link

        result = download_link("dl", "Download")
        assert isinstance(result, Tag)
        assert result.name == "a"
        assert result.attrs.get("id") == "dl"

    def test_download_link_with_label(self):
        """download_link should display label."""
        from shiny.ui import download_link

        result = download_link("dl", "Download File")
        html_str = str(result)
        assert "Download File" in html_str

    def test_download_link_with_icon(self):
        """download_link should include icon."""
        from shiny.ui import download_link

        result = download_link("dl", "Download", icon="📥")
        html_str = str(result)
        assert "📥" in html_str

    def test_download_link_has_shiny_download_link_class(self):
        """download_link should have shiny-download-link class."""
        from shiny.ui import download_link

        result = download_link("dl", "Download")
        assert "shiny-download-link" in result.attrs.get("class", "")

    def test_download_link_no_btn_class(self):
        """download_link should not have btn classes."""
        from shiny.ui import download_link

        result = download_link("dl", "Download")
        class_attr = result.attrs.get("class", "")
        assert "btn" not in class_attr or "btn-" not in class_attr

    def test_download_link_is_disabled_initially(self):
        """download_link should be disabled initially."""
        from shiny.ui import download_link

        result = download_link("dl", "Download")
        assert "disabled" in result.attrs.get("class", "")
        assert result.attrs.get("aria-disabled") == "true"
        assert result.attrs.get("tabindex") == "-1"

    def test_download_link_has_empty_href(self):
        """download_link should have empty href initially."""
        from shiny.ui import download_link

        result = download_link("dl", "Download")
        assert result.attrs.get("href") == ""

    def test_download_link_has_target_blank(self):
        """download_link should open in new tab."""
        from shiny.ui import download_link

        result = download_link("dl", "Download")
        assert result.attrs.get("target") == "_blank"

    def test_download_link_with_width(self):
        """download_link should accept width parameter."""
        from shiny.ui import download_link

        result = download_link("dl", "Download", width="200px")
        html_str = str(result)
        assert "200px" in html_str

    def test_download_link_with_kwargs(self):
        """download_link should accept additional attributes."""
        from shiny.ui import download_link

        result = download_link("dl", "Download", data_value="test")
        assert result.attrs.get("data-value") == "test"


class TestModuleExports:
    """Tests for module exports."""

    def test_module_imports_correctly(self):
        """Module should import without errors."""
        import shiny.ui._download_button as download_button_module

        assert download_button_module is not None

    def test_all_exports_exist(self):
        """All items in __all__ should be importable."""
        from shiny.ui import _download_button

        for item in _download_button.__all__:
            assert hasattr(_download_button, item)
