"""Tests for shiny/ui/_page.py"""

from htmltools import Tag

from shiny.ui import (
    page_bootstrap,
    page_fillable,
    page_fixed,
    page_fluid,
)


class TestPageFluid:
    """Tests for the page_fluid function."""

    def test_basic_page_fluid(self):
        """Test basic fluid page creation."""
        result = page_fluid("Content")
        html = str(result)
        assert "Content" in html
        assert "container-fluid" in html

    def test_page_fluid_returns_tag(self):
        """Test page_fluid returns a Tag."""
        result = page_fluid("Content")
        assert isinstance(result, Tag)

    def test_page_fluid_with_title(self):
        """Test fluid page with title."""
        result = page_fluid("Content", title="My App")
        html = str(result)
        assert "My App" in html

    def test_page_fluid_with_multiple_children(self):
        """Test fluid page with multiple children."""
        result = page_fluid("Child 1", "Child 2", "Child 3")
        html = str(result)
        assert "Child 1" in html
        assert "Child 2" in html
        assert "Child 3" in html

    def test_page_fluid_with_lang(self):
        """Test fluid page with language."""
        result = page_fluid("Content", lang="en")
        html = str(result)
        assert 'lang="en"' in html


class TestPageFixed:
    """Tests for the page_fixed function."""

    def test_basic_page_fixed(self):
        """Test basic fixed page creation."""
        result = page_fixed("Content")
        html = str(result)
        assert "Content" in html
        # Fixed pages use container (not container-fluid)

    def test_page_fixed_returns_tag(self):
        """Test page_fixed returns a Tag."""
        result = page_fixed("Content")
        assert isinstance(result, Tag)

    def test_page_fixed_with_title(self):
        """Test fixed page with title."""
        result = page_fixed("Content", title="My App")
        html = str(result)
        assert "My App" in html

    def test_page_fixed_with_lang(self):
        """Test fixed page with language."""
        result = page_fixed("Content", lang="ko")
        html = str(result)
        assert 'lang="ko"' in html


class TestPageFillable:
    """Tests for the page_fillable function."""

    def test_basic_page_fillable(self):
        """Test basic fillable page creation."""
        result = page_fillable("Content")
        html = str(result)
        assert "Content" in html
        assert "html-fill-container" in html

    def test_page_fillable_returns_tag(self):
        """Test page_fillable returns a Tag."""
        result = page_fillable("Content")
        assert isinstance(result, Tag)

    def test_page_fillable_with_title(self):
        """Test fillable page with title."""
        result = page_fillable("Content", title="My App")
        html = str(result)
        assert "My App" in html

    def test_page_fillable_with_padding(self):
        """Test fillable page with padding."""
        result = page_fillable("Content", padding="20px")
        html = str(result)
        assert "padding" in html

    def test_page_fillable_with_gap(self):
        """Test fillable page with gap."""
        result = page_fillable("Content", gap="10px")
        html = str(result)
        assert "gap" in html

    def test_page_fillable_fillable_mobile_true(self):
        """Test fillable page with fillable_mobile enabled."""
        result = page_fillable("Content", fillable_mobile=True)
        assert isinstance(result, Tag)

    def test_page_fillable_fillable_mobile_false(self):
        """Test fillable page with fillable_mobile disabled."""
        result = page_fillable("Content", fillable_mobile=False)
        assert isinstance(result, Tag)


class TestPageBootstrap:
    """Tests for the page_bootstrap function."""

    def test_basic_page_bootstrap(self):
        """Test basic bootstrap page creation."""
        result = page_bootstrap("Content")
        html = str(result)
        assert "Content" in html

    def test_page_bootstrap_returns_tag(self):
        """Test page_bootstrap returns a Tag."""
        result = page_bootstrap("Content")
        assert isinstance(result, Tag)

    def test_page_bootstrap_with_title(self):
        """Test bootstrap page with title."""
        result = page_bootstrap("Content", title="My App")
        html = str(result)
        assert "My App" in html

    def test_page_bootstrap_with_lang(self):
        """Test bootstrap page with language."""
        result = page_bootstrap("Content", lang="fr")
        html = str(result)
        assert 'lang="fr"' in html

    def test_page_bootstrap_with_multiple_children(self):
        """Test bootstrap page with multiple children."""
        result = page_bootstrap("Child 1", "Child 2")
        html = str(result)
        assert "Child 1" in html
        assert "Child 2" in html
