"""Tests for shiny.experimental.ui._deprecated module."""

import warnings

from htmltools import Tag, tags

from shiny.experimental.ui._deprecated import card, card_body, card_title


class TestExperimentalCard:
    """Tests for deprecated card function."""

    def test_card_returns_tag(self):
        """card should return a Tag and emit deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = card("Content")
            # Should have at least one warning
            assert len(w) >= 1
            # Should be a deprecation warning
            assert any("deprecated" in str(warning.message).lower() for warning in w)
            # Result should be a Tag
            assert isinstance(result, Tag)

    def test_card_with_full_screen(self):
        """card should accept full_screen parameter."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = card("Content", full_screen=True)
            assert isinstance(result, Tag)

    def test_card_with_height(self):
        """card should accept height parameter."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = card("Content", height="300px")
            assert isinstance(result, Tag)

    def test_card_with_class(self):
        """card should accept class_ parameter."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = card("Content", class_="my-card")
            html = str(result)
            assert "my-card" in html


class TestExperimentalCardBody:
    """Tests for deprecated card_body function."""

    def test_card_body_returns_card_item(self):
        """card_body should return a CardItem and emit deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = card_body("Content")
            # Should have at least one warning
            assert len(w) >= 1
            # Should be a deprecation warning
            assert any("deprecated" in str(warning.message).lower() for warning in w)
            # Result should not be None
            assert result is not None

    def test_card_body_with_fillable(self):
        """card_body should accept fillable parameter."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = card_body("Content", fillable=False)
            assert result is not None

    def test_card_body_with_height(self):
        """card_body should accept height parameter."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = card_body("Content", height="200px")
            assert result is not None

    def test_card_body_with_padding(self):
        """card_body should accept padding parameter."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = card_body("Content", padding="10px")
            assert result is not None


class TestExperimentalCardTitle:
    """Tests for deprecated card_title function."""

    def test_card_title_returns_tagifiable(self):
        """card_title should return a Tagifiable and emit deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = card_title("My Title")
            # Should have at least one warning
            assert len(w) >= 1
            # Should be a deprecation warning
            assert any("deprecated" in str(warning.message).lower() for warning in w)
            # Result should be renderable
            html = str(result)
            assert "My Title" in html

    def test_card_title_default_container_is_h5(self):
        """card_title should use h5 as default container."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = card_title("Title")
            html = str(result)
            assert "<h5" in html

    def test_card_title_with_custom_container(self):
        """card_title should accept custom container."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = card_title("Title", container=tags.h3)
            html = str(result)
            assert "<h3" in html

    def test_card_title_with_class(self):
        """card_title should accept class attribute."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = card_title("Title", class_="my-title")
            html = str(result)
            assert "my-title" in html
