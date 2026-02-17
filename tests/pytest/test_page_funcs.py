"""Tests for shiny.ui._page module."""

from htmltools import Tag

from shiny.ui._page import (
    page_auto,
    page_bootstrap,
    page_fillable,
    page_fixed,
    page_fluid,
)


class TestPageFluid:
    """Tests for page_fluid function."""

    def test_page_fluid_basic(self) -> None:
        """Test basic page_fluid creation."""
        result = page_fluid("Content")
        assert isinstance(result, Tag)

    def test_page_fluid_with_content(self) -> None:
        """Test page_fluid with content."""
        result = page_fluid("Page content")
        html = str(result)
        assert "Page content" in html

    def test_page_fluid_with_title(self) -> None:
        """Test page_fluid with title."""
        result = page_fluid("Content", title="My Page")
        html = str(result)
        assert "My Page" in html

    def test_page_fluid_is_html(self) -> None:
        """Test page_fluid returns html tag."""
        result = page_fluid("Content")
        assert result.name == "html"

    def test_page_fluid_with_lang(self) -> None:
        """Test page_fluid with lang parameter."""
        result = page_fluid("Content", lang="en")
        html = str(result)
        assert 'lang="en"' in html


class TestPageFixed:
    """Tests for page_fixed function."""

    def test_page_fixed_basic(self) -> None:
        """Test basic page_fixed creation."""
        result = page_fixed("Content")
        assert isinstance(result, Tag)

    def test_page_fixed_with_content(self) -> None:
        """Test page_fixed with content."""
        result = page_fixed("Page content")
        html = str(result)
        assert "Page content" in html

    def test_page_fixed_with_title(self) -> None:
        """Test page_fixed with title."""
        result = page_fixed("Content", title="Fixed Page")
        html = str(result)
        assert "Fixed Page" in html


class TestPageFillable:
    """Tests for page_fillable function."""

    def test_page_fillable_basic(self) -> None:
        """Test basic page_fillable creation."""
        result = page_fillable("Content")
        assert isinstance(result, Tag)

    def test_page_fillable_with_content(self) -> None:
        """Test page_fillable with content."""
        result = page_fillable("Fillable content")
        html = str(result)
        assert "Fillable content" in html

    def test_page_fillable_with_title(self) -> None:
        """Test page_fillable with title."""
        result = page_fillable("Content", title="Fillable Page")
        html = str(result)
        assert "Fillable Page" in html

    def test_page_fillable_with_padding(self) -> None:
        """Test page_fillable with padding parameter."""
        result = page_fillable("Content", padding="20px")
        html = str(result)
        assert "Content" in html

    def test_page_fillable_fillable_mobile(self) -> None:
        """Test page_fillable with fillable_mobile parameter."""
        result = page_fillable("Content", fillable_mobile=True)
        html = str(result)
        assert "Content" in html


class TestPageBootstrap:
    """Tests for page_bootstrap function."""

    def test_page_bootstrap_basic(self) -> None:
        """Test basic page_bootstrap creation."""
        result = page_bootstrap("Content")
        assert isinstance(result, Tag)

    def test_page_bootstrap_with_content(self) -> None:
        """Test page_bootstrap with content."""
        result = page_bootstrap("Bootstrap content")
        html = str(result)
        assert "Bootstrap content" in html

    def test_page_bootstrap_with_title(self) -> None:
        """Test page_bootstrap with title."""
        result = page_bootstrap("Content", title="Bootstrap Page")
        html = str(result)
        assert "Bootstrap Page" in html


class TestPageAuto:
    """Tests for page_auto function."""

    def test_page_auto_basic(self) -> None:
        """Test basic page_auto creation."""
        result = page_auto("Content")
        assert isinstance(result, Tag)

    def test_page_auto_with_content(self) -> None:
        """Test page_auto with content."""
        result = page_auto("Auto page content")
        html = str(result)
        assert "Auto page content" in html

    def test_page_auto_with_title(self) -> None:
        """Test page_auto with title."""
        result = page_auto("Content", title="Auto Page")
        html = str(result)
        assert "Auto Page" in html

    def test_page_auto_with_fillable(self) -> None:
        """Test page_auto with fillable parameter."""
        result = page_auto("Content", fillable=True)
        html = str(result)
        assert "Content" in html
