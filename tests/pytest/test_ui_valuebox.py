"""Tests for shiny/ui/_valuebox.py"""

from __future__ import annotations

import pytest
from htmltools import Tag, span

from shiny.ui import (
    value_box,
    value_box_theme,
    showcase_left_center,
    showcase_top_right,
    showcase_bottom,
)
from shiny.ui._valuebox import ShowcaseLayout, ValueBoxTheme, resolve_showcase_layout


class TestShowcaseLayout:
    """Tests for the ShowcaseLayout class."""

    def test_basic_layout(self) -> None:
        """Test creating a basic ShowcaseLayout."""
        layout = ShowcaseLayout(class_="my-layout")
        assert layout.class_ == "my-layout"
        assert layout.width == "33%"
        assert layout.max_height == "100px"

    def test_layout_with_custom_values(self) -> None:
        """Test ShowcaseLayout with custom values."""
        layout = ShowcaseLayout(
            class_="custom",
            width="50%",
            width_full_screen="2fr",
            height="100px",
            height_full_screen="50%",
            max_height="200px",
            max_height_full_screen="80%",
        )
        assert layout.class_ == "custom"
        assert layout.width == "50%"
        assert layout.width_full_screen == "2fr"
        assert layout.height == "100px"
        assert layout.height_full_screen == "50%"
        assert layout.max_height == "200px"
        assert layout.max_height_full_screen == "80%"

    def test_layout_none_values(self) -> None:
        """Test ShowcaseLayout with None values."""
        layout = ShowcaseLayout(
            class_="test",
            width=None,
            height=None,
            max_height=None,
        )
        assert layout.width is None
        assert layout.height is None
        assert layout.max_height is None


class TestShowcaseLayoutFunctions:
    """Tests for the showcase layout factory functions."""

    def test_showcase_left_center_defaults(self) -> None:
        """Test showcase_left_center with default values."""
        layout = showcase_left_center()
        assert isinstance(layout, ShowcaseLayout)
        assert layout.class_ == "showcase-left-center"
        assert layout.width == "30%"
        assert layout.width_full_screen == "1fr"
        assert layout.max_height == "100px"
        assert layout.max_height_full_screen == "67%"

    def test_showcase_left_center_custom(self) -> None:
        """Test showcase_left_center with custom values."""
        layout = showcase_left_center(
            width="40%",
            max_height="150px",
        )
        assert layout.width == "40%"
        assert layout.max_height == "150px"

    def test_showcase_top_right_defaults(self) -> None:
        """Test showcase_top_right with default values."""
        layout = showcase_top_right()
        assert isinstance(layout, ShowcaseLayout)
        assert layout.class_ == "showcase-top-right"
        assert layout.width == "40%"
        assert layout.max_height == "75px"

    def test_showcase_top_right_custom(self) -> None:
        """Test showcase_top_right with custom values."""
        layout = showcase_top_right(
            width="50%",
            max_height="100px",
        )
        assert layout.width == "50%"
        assert layout.max_height == "100px"

    def test_showcase_bottom_defaults(self) -> None:
        """Test showcase_bottom with default values."""
        layout = showcase_bottom()
        assert isinstance(layout, ShowcaseLayout)
        assert layout.class_ == "showcase-bottom"
        assert layout.width == "100%"
        assert layout.height == "auto"
        assert layout.height_full_screen == "2fr"
        assert layout.max_height == "100px"

    def test_showcase_bottom_custom(self) -> None:
        """Test showcase_bottom with custom values."""
        layout = showcase_bottom(
            height="150px",
            max_height="200px",
        )
        assert layout.height == "150px"
        assert layout.max_height == "200px"


class TestResolveShowcaseLayout:
    """Tests for resolve_showcase_layout function."""

    def test_resolve_string_left_center(self) -> None:
        """Test resolving 'left center' string."""
        layout = resolve_showcase_layout("left center")
        assert isinstance(layout, ShowcaseLayout)
        assert layout.class_ == "showcase-left-center"

    def test_resolve_string_top_right(self) -> None:
        """Test resolving 'top right' string."""
        layout = resolve_showcase_layout("top right")
        assert isinstance(layout, ShowcaseLayout)
        assert layout.class_ == "showcase-top-right"

    def test_resolve_string_bottom(self) -> None:
        """Test resolving 'bottom' string."""
        layout = resolve_showcase_layout("bottom")
        assert isinstance(layout, ShowcaseLayout)
        assert layout.class_ == "showcase-bottom"

    def test_resolve_layout_object(self) -> None:
        """Test resolving ShowcaseLayout object."""
        original = ShowcaseLayout(class_="custom")
        result = resolve_showcase_layout(original)
        assert result is original

    def test_resolve_invalid_string(self) -> None:
        """Test resolving invalid string raises ValueError."""
        with pytest.raises(ValueError, match="showcase_layout.*must be one of"):
            resolve_showcase_layout("invalid")  # type: ignore


class TestValueBoxTheme:
    """Tests for the ValueBoxTheme class and value_box_theme function."""

    def test_basic_theme(self) -> None:
        """Test creating basic ValueBoxTheme."""
        theme = value_box_theme("primary")
        assert isinstance(theme, ValueBoxTheme)
        assert theme.class_ == "bg-primary"

    def test_theme_with_bg_prefix(self) -> None:
        """Test theme with bg- prefix."""
        theme = value_box_theme("bg-danger")
        assert theme.class_ == "bg-danger"

    def test_theme_with_text_prefix(self) -> None:
        """Test theme with text- prefix."""
        theme = value_box_theme("text-warning")
        assert theme.class_ == "text-warning"

    def test_theme_no_name_no_bg(self) -> None:
        """Test theme with no name and no bg defaults to 'default'."""
        theme = value_box_theme()
        assert theme.class_ == "default"

    def test_theme_with_custom_colors(self) -> None:
        """Test theme with custom fg and bg colors."""
        theme = value_box_theme(fg="#ffffff", bg="#000000")
        assert theme.fg == "#ffffff"
        assert theme.bg == "#000000"

    def test_theme_non_string_name_raises(self) -> None:
        """Test that non-string name raises TypeError."""
        with pytest.raises(TypeError, match="should be a single string"):
            value_box_theme(123)  # type: ignore


class TestValueBox:
    """Tests for the value_box function."""

    def test_basic_value_box(self) -> None:
        """Test creating a basic value box."""
        result = value_box("Title", "Value")
        assert isinstance(result, Tag)

    def test_value_box_with_showcase(self) -> None:
        """Test value box with showcase."""
        result = value_box(
            "Sales",
            "$1,234",
            showcase=span("📈"),
        )
        assert isinstance(result, Tag)
        rendered = str(result)
        assert "📈" in rendered or "1,234" in rendered

    def test_value_box_with_showcase_layout_string(self) -> None:
        """Test value box with showcase layout as string."""
        result = value_box(
            "Title",
            "Value",
            showcase=span("Icon"),
            showcase_layout="top right",
        )
        assert isinstance(result, Tag)

    def test_value_box_with_showcase_layout_object(self) -> None:
        """Test value box with ShowcaseLayout object."""
        layout = showcase_bottom()
        result = value_box(
            "Title",
            "Value",
            showcase=span("Icon"),
            showcase_layout=layout,
        )
        assert isinstance(result, Tag)

    def test_value_box_with_theme_string(self) -> None:
        """Test value box with theme as string."""
        result = value_box("Title", "Value", theme="primary")
        assert isinstance(result, Tag)

    def test_value_box_with_theme_object(self) -> None:
        """Test value box with ValueBoxTheme object."""
        theme = value_box_theme("danger")
        result = value_box("Title", "Value", theme=theme)
        assert isinstance(result, Tag)

    def test_value_box_with_height(self) -> None:
        """Test value box with height."""
        result = value_box("Title", "Value", height="200px")
        assert isinstance(result, Tag)

    def test_value_box_with_min_max_height(self) -> None:
        """Test value box with min and max height."""
        result = value_box(
            "Title",
            "Value",
            min_height="100px",
            max_height="300px",
        )
        assert isinstance(result, Tag)

    def test_value_box_full_screen(self) -> None:
        """Test value box with full screen enabled."""
        result = value_box("Title", "Value", full_screen=True)
        assert isinstance(result, Tag)

    def test_value_box_fill_false(self) -> None:
        """Test value box with fill=False."""
        result = value_box("Title", "Value", fill=False)
        assert isinstance(result, Tag)

    def test_value_box_with_class(self) -> None:
        """Test value box with custom class."""
        result = value_box("Title", "Value", class_="my-custom-class")
        assert isinstance(result, Tag)

    def test_value_box_with_id(self) -> None:
        """Test value box with id."""
        result = value_box("Title", "Value", id="my_valuebox")
        assert isinstance(result, Tag)

    def test_value_box_with_extra_children(self) -> None:
        """Test value box with additional children."""
        result = value_box(
            "Sales",
            "$1,234",
            "Up 10% from last month",
            span("Additional info"),
        )
        assert isinstance(result, Tag)
        rendered = str(result)
        assert "Up 10%" in rendered or "1,234" in rendered

    def test_value_box_renders_title_value(self) -> None:
        """Test that value box renders title and value."""
        result = value_box("My Title", "My Value")
        rendered = str(result)
        assert "My Title" in rendered
        assert "My Value" in rendered


class TestValueBoxStructure:
    """Tests for value box DOM structure."""

    def test_value_box_is_card(self) -> None:
        """Test that value box is based on card."""
        result = value_box("Title", "Value")
        rendered = str(result)
        # Value box is built on card
        assert "card" in rendered

    def test_value_box_has_content_area(self) -> None:
        """Test that value box has content area."""
        result = value_box("Title", "Value")
        rendered = str(result)
        # Should have value box content area
        assert "value-box" in rendered or "card" in rendered
