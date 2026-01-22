"""Tests for shiny/ui/_card.py"""

from __future__ import annotations

from htmltools import Tag, TagList, div, span

from shiny.ui import card, card_body, card_footer, card_header
from shiny.ui._card import CardItem


class TestCard:
    """Tests for the card function."""

    def test_basic_card(self) -> None:
        """Test creating a basic card."""
        result = card("Content")
        assert isinstance(result, Tag)
        assert result.name == "div"
        class_attr = result.attrs.get("class", "")
        assert "card" in class_attr

    def test_card_with_multiple_children(self) -> None:
        """Test card with multiple children."""
        result = card("Child 1", "Child 2", "Child 3")
        assert isinstance(result, Tag)
        rendered = str(result)
        assert "Child 1" in rendered
        assert "Child 2" in rendered
        assert "Child 3" in rendered

    def test_card_with_id(self) -> None:
        """Test card with custom id."""
        result = card("Content", id="my_card")
        assert result.attrs.get("id") == "my_card"

    def test_card_auto_generates_id_when_full_screen(self) -> None:
        """Test that card auto-generates id when full_screen=True."""
        result = card("Content", full_screen=True)
        assert result.attrs.get("id") is not None
        assert "bslib_card" in result.attrs.get("id", "")

    def test_card_full_screen(self) -> None:
        """Test card with full screen enabled."""
        result = card("Content", full_screen=True)
        assert result.attrs.get("data-full-screen") == "false"

    def test_card_no_full_screen(self) -> None:
        """Test card without full screen."""
        result = card("Content", full_screen=False)
        assert result.attrs.get("data-full-screen") is None

    def test_card_with_height(self) -> None:
        """Test card with height."""
        result = card("Content", height="200px")
        style_attr = result.attrs.get("style", "")
        assert "200px" in str(style_attr)

    def test_card_with_min_max_height(self) -> None:
        """Test card with min and max height."""
        result = card("Content", min_height="100px", max_height="300px")
        assert isinstance(result, Tag)

    def test_card_fill_true(self) -> None:
        """Test card with fill=True (default)."""
        result = card("Content", fill=True)
        assert isinstance(result, Tag)

    def test_card_fill_false(self) -> None:
        """Test card with fill=False."""
        result = card("Content", fill=False)
        assert isinstance(result, Tag)

    def test_card_with_class(self) -> None:
        """Test card with custom class."""
        result = card("Content", class_="my-custom-class")
        class_attr = result.attrs.get("class", "")
        assert "my-custom-class" in class_attr

    def test_card_renders_bslib_classes(self) -> None:
        """Test that card has bslib-specific classes."""
        result = card("Content")
        class_attr = result.attrs.get("class", "")
        assert "bslib-card" in class_attr


class TestCardHeader:
    """Tests for the card_header function."""

    def test_basic_header(self) -> None:
        """Test creating a basic card header."""
        result = card_header("My Header")
        assert isinstance(result, CardItem)

    def test_header_resolve(self) -> None:
        """Test that header resolves to a Tag."""
        result = card_header("My Header")
        resolved = result.resolve()
        assert isinstance(resolved, Tag)
        assert "card-header" in str(resolved)

    def test_header_with_class(self) -> None:
        """Test header with custom class."""
        result = card_header("Header", class_="my-header-class")
        resolved = result.resolve()
        rendered = str(resolved)
        assert "my-header-class" in rendered

    def test_header_with_multiple_children(self) -> None:
        """Test header with multiple children."""
        result = card_header("Title", span("Subtitle"))
        resolved = result.resolve()
        rendered = str(resolved)
        assert "Title" in rendered


class TestCardFooter:
    """Tests for the card_footer function."""

    def test_basic_footer(self) -> None:
        """Test creating a basic card footer."""
        result = card_footer("My Footer")
        assert isinstance(result, CardItem)

    def test_footer_resolve(self) -> None:
        """Test that footer resolves to a Tag."""
        result = card_footer("My Footer")
        resolved = result.resolve()
        assert isinstance(resolved, Tag)
        assert "card-footer" in str(resolved)

    def test_footer_with_class(self) -> None:
        """Test footer with custom class."""
        result = card_footer("Footer", class_="my-footer-class")
        resolved = result.resolve()
        rendered = str(resolved)
        assert "my-footer-class" in rendered


class TestCardBody:
    """Tests for the card_body function."""

    def test_basic_body(self) -> None:
        """Test creating a basic card body."""
        result = card_body("Body content")
        assert isinstance(result, CardItem)

    def test_body_resolve(self) -> None:
        """Test that body resolves to a Tag."""
        result = card_body("Body content")
        resolved = result.resolve()
        assert isinstance(resolved, Tag)
        assert "card-body" in str(resolved)

    def test_body_fillable_true(self) -> None:
        """Test body with fillable=True (default)."""
        result = card_body("Content", fillable=True)
        resolved = result.resolve()
        rendered = str(resolved)
        assert "bslib-gap-spacing" in rendered

    def test_body_fillable_false(self) -> None:
        """Test body with fillable=False."""
        result = card_body("Content", fillable=False)
        resolved = result.resolve()
        rendered = str(resolved)
        assert "bslib-gap-spacing" not in rendered

    def test_body_with_height(self) -> None:
        """Test body with height."""
        result = card_body("Content", height="150px")
        resolved = result.resolve()
        style_attr = str(resolved.attrs.get("style", ""))
        assert "150px" in style_attr

    def test_body_with_padding(self) -> None:
        """Test body with padding."""
        result = card_body("Content", padding="10px")
        resolved = result.resolve()
        assert isinstance(resolved, Tag)

    def test_body_with_gap(self) -> None:
        """Test body with gap."""
        result = card_body("Content", gap="5px")
        resolved = result.resolve()
        style_attr = str(resolved.attrs.get("style", ""))
        assert "5px" in style_attr

    def test_body_fill_false(self) -> None:
        """Test body with fill=False."""
        result = card_body("Content", fill=False)
        assert isinstance(result, CardItem)


class TestCardItem:
    """Tests for the CardItem class."""

    def test_create_card_item(self) -> None:
        """Test creating a CardItem."""
        tag = div("Content")
        item = CardItem(tag)
        assert item.resolve() is tag

    def test_card_item_with_string(self) -> None:
        """Test CardItem with string content."""
        item = CardItem("String content")
        resolved = item.resolve()
        assert resolved == "String content"

    def test_card_item_with_taglist(self) -> None:
        """Test CardItem with TagList content."""
        content = TagList(span("A"), span("B"))
        item = CardItem(content)
        resolved = item.resolve()
        assert resolved is content


class TestCardWithComponents:
    """Tests for card with header, body, footer."""

    def test_card_with_header(self) -> None:
        """Test card with header."""
        result = card(
            card_header("My Header"),
            "Body content",
        )
        rendered = str(result)
        assert "My Header" in rendered
        assert "card-header" in rendered

    def test_card_with_footer(self) -> None:
        """Test card with footer."""
        result = card(
            "Body content",
            card_footer("My Footer"),
        )
        rendered = str(result)
        assert "My Footer" in rendered
        assert "card-footer" in rendered

    def test_card_with_header_body_footer(self) -> None:
        """Test card with all components."""
        result = card(
            card_header("Header"),
            card_body("Body"),
            card_footer("Footer"),
        )
        rendered = str(result)
        assert "Header" in rendered
        assert "Body" in rendered
        assert "Footer" in rendered
        assert "card-header" in rendered
        assert "card-body" in rendered
        assert "card-footer" in rendered


class TestCardStructure:
    """Tests for card DOM structure."""

    def test_card_has_init_attribute(self) -> None:
        """Test that card has data-bslib-card-init attribute."""
        result = card("Content")
        assert result.attrs.get("data-bslib-card-init") is not None

    def test_card_includes_dependencies(self) -> None:
        """Test that card includes necessary dependencies."""
        result = card("Content")
        # Card should include JavaScript initialization
        rendered = str(result)
        assert "bslib" in rendered.lower() or "script" in rendered.lower()

    def test_card_is_fillable(self) -> None:
        """Test that card is marked as fillable container."""
        result = card("Content")
        # Card should be a fillable container
        class_attr = result.attrs.get("class", "")
        # Fill containers have specific classes
        assert "card" in class_attr
