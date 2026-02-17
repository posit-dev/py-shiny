"""Unit tests for shiny.ui._valuebox module."""

from __future__ import annotations

from htmltools import Tag, tags

from shiny.ui import (
    ShowcaseLayout,
    showcase_bottom,
    showcase_left_center,
    showcase_top_right,
    value_box,
    value_box_theme,
)


class TestShowcaseLayout:
    """Tests for ShowcaseLayout class."""

    def test_showcase_layout_init(self) -> None:
        """Test ShowcaseLayout initialization."""
        layout = ShowcaseLayout(class_="test-class")
        assert layout.class_ == "test-class"

    def test_showcase_layout_default_width(self) -> None:
        """Test ShowcaseLayout default width."""
        layout = ShowcaseLayout(class_="test-class")
        assert layout.width == "33%"

    def test_showcase_layout_default_max_height(self) -> None:
        """Test ShowcaseLayout default max_height."""
        layout = ShowcaseLayout(class_="test-class")
        assert layout.max_height == "100px"

    def test_showcase_layout_custom_width(self) -> None:
        """Test ShowcaseLayout with custom width."""
        layout = ShowcaseLayout(class_="test", width="50%")
        assert layout.width == "50%"

    def test_showcase_layout_custom_height(self) -> None:
        """Test ShowcaseLayout with custom height."""
        layout = ShowcaseLayout(class_="test", height="200px")
        assert layout.height == "200px"


class TestShowcaseLeftCenter:
    """Tests for showcase_left_center function."""

    def test_basic_showcase_left_center(self) -> None:
        """Test basic showcase_left_center."""
        layout = showcase_left_center()
        assert isinstance(layout, ShowcaseLayout)
        assert layout.class_ == "showcase-left-center"

    def test_showcase_left_center_default_width(self) -> None:
        """Test showcase_left_center default width."""
        layout = showcase_left_center()
        assert layout.width == "30%"

    def test_showcase_left_center_default_max_height(self) -> None:
        """Test showcase_left_center default max_height."""
        layout = showcase_left_center()
        assert layout.max_height == "100px"

    def test_showcase_left_center_custom_width(self) -> None:
        """Test showcase_left_center with custom width."""
        layout = showcase_left_center(width="40%")
        assert layout.width == "40%"

    def test_showcase_left_center_custom_max_height(self) -> None:
        """Test showcase_left_center with custom max_height."""
        layout = showcase_left_center(max_height="150px")
        assert layout.max_height == "150px"


class TestShowcaseTopRight:
    """Tests for showcase_top_right function."""

    def test_basic_showcase_top_right(self) -> None:
        """Test basic showcase_top_right."""
        layout = showcase_top_right()
        assert isinstance(layout, ShowcaseLayout)
        assert layout.class_ == "showcase-top-right"

    def test_showcase_top_right_default_width(self) -> None:
        """Test showcase_top_right default width."""
        layout = showcase_top_right()
        assert layout.width == "40%"

    def test_showcase_top_right_default_max_height(self) -> None:
        """Test showcase_top_right default max_height."""
        layout = showcase_top_right()
        assert layout.max_height == "75px"

    def test_showcase_top_right_custom_width(self) -> None:
        """Test showcase_top_right with custom width."""
        layout = showcase_top_right(width="50%")
        assert layout.width == "50%"


class TestShowcaseBottom:
    """Tests for showcase_bottom function."""

    def test_basic_showcase_bottom(self) -> None:
        """Test basic showcase_bottom."""
        layout = showcase_bottom()
        assert isinstance(layout, ShowcaseLayout)
        assert layout.class_ == "showcase-bottom"

    def test_showcase_bottom_default_width(self) -> None:
        """Test showcase_bottom default width."""
        layout = showcase_bottom()
        assert layout.width == "100%"

    def test_showcase_bottom_default_height(self) -> None:
        """Test showcase_bottom default height."""
        layout = showcase_bottom()
        assert layout.height == "auto"

    def test_showcase_bottom_default_max_height(self) -> None:
        """Test showcase_bottom default max_height."""
        layout = showcase_bottom()
        assert layout.max_height == "100px"


class TestValueBoxTheme:
    """Tests for value_box_theme function."""

    def test_value_box_theme_with_name(self) -> None:
        """Test value_box_theme with name."""
        theme = value_box_theme("primary")
        assert theme.class_ == "bg-primary"

    def test_value_box_theme_with_bg_prefix(self) -> None:
        """Test value_box_theme with bg- prefix."""
        theme = value_box_theme("bg-danger")
        assert theme.class_ == "bg-danger"

    def test_value_box_theme_with_text_prefix(self) -> None:
        """Test value_box_theme with text- prefix."""
        theme = value_box_theme("text-success")
        assert theme.class_ == "text-success"

    def test_value_box_theme_with_fg_bg(self) -> None:
        """Test value_box_theme with custom fg and bg."""
        theme = value_box_theme(fg="white", bg="blue")
        assert theme.fg == "white"
        assert theme.bg == "blue"

    def test_value_box_theme_default(self) -> None:
        """Test value_box_theme default."""
        theme = value_box_theme()
        assert theme.class_ == "default"


class TestValueBox:
    """Tests for value_box function."""

    def test_basic_value_box(self) -> None:
        """Test basic value_box."""
        result = value_box("Title", "100")
        assert isinstance(result, Tag)
        html = str(result)
        assert "Title" in html
        assert "100" in html

    def test_value_box_returns_tag(self) -> None:
        """Test that value_box returns a Tag."""
        result = value_box("Title", "Value")
        assert isinstance(result, Tag)

    def test_value_box_with_showcase(self) -> None:
        """Test value_box with showcase."""
        icon = tags.i(class_="fa fa-chart-line")
        result = value_box("Sales", "$1,000", showcase=icon)
        html = str(result)
        assert "fa-chart-line" in html

    def test_value_box_showcase_layout_string(self) -> None:
        """Test value_box with showcase_layout as string."""
        icon = tags.i(class_="fa fa-users")
        result = value_box("Users", "500", showcase=icon, showcase_layout="top right")
        html = str(result)
        assert "Users" in html
        assert "500" in html

    def test_value_box_showcase_layout_bottom(self) -> None:
        """Test value_box with bottom showcase layout."""
        icon = tags.i(class_="fa fa-dollar")
        result = value_box("Revenue", "$5,000", showcase=icon, showcase_layout="bottom")
        html = str(result)
        assert "Revenue" in html

    def test_value_box_showcase_layout_object(self) -> None:
        """Test value_box with ShowcaseLayout object."""
        layout = showcase_left_center(width="40%")
        icon = tags.i(class_="fa fa-star")
        result = value_box("Rating", "4.5", showcase=icon, showcase_layout=layout)
        html = str(result)
        assert "Rating" in html

    def test_value_box_full_screen(self) -> None:
        """Test value_box with full_screen enabled."""
        result = value_box("Title", "Value", full_screen=True)
        html = str(result)
        assert "full-screen" in html.lower()

    def test_value_box_with_theme_string(self) -> None:
        """Test value_box with theme as string."""
        result = value_box("Title", "Value", theme="primary")
        html = str(result)
        assert "bg-primary" in html

    def test_value_box_with_theme_object(self) -> None:
        """Test value_box with ValueBoxTheme object."""
        theme = value_box_theme("danger")
        result = value_box("Title", "Value", theme=theme)
        html = str(result)
        assert "danger" in html

    def test_value_box_height(self) -> None:
        """Test value_box with height parameter."""
        result = value_box("Title", "Value", height="200px")
        html = str(result)
        assert "200px" in html

    def test_value_box_max_height(self) -> None:
        """Test value_box with max_height parameter."""
        result = value_box("Title", "Value", max_height="300px")
        html = str(result)
        assert "300px" in html

    def test_value_box_min_height(self) -> None:
        """Test value_box with min_height parameter."""
        result = value_box("Title", "Value", min_height="100px")
        html = str(result)
        assert "100px" in html

    def test_value_box_fill_true(self) -> None:
        """Test value_box with fill=True (default)."""
        result = value_box("Title", "Value", fill=True)
        html = str(result)
        assert "value-box" in html.lower()

    def test_value_box_fill_false(self) -> None:
        """Test value_box with fill=False."""
        result = value_box("Title", "Value", fill=False)
        html = str(result)
        assert "value-box" in html.lower()

    def test_value_box_with_class(self) -> None:
        """Test value_box with custom class."""
        result = value_box("Title", "Value", class_="custom-valuebox")
        html = str(result)
        assert "custom-valuebox" in html

    def test_value_box_with_id(self) -> None:
        """Test value_box with id."""
        result = value_box("Title", "Value", id="my_valuebox")
        html = str(result)
        assert "my_valuebox" in html

    def test_value_box_with_extra_content(self) -> None:
        """Test value_box with extra content."""
        result = value_box(
            "Title",
            "Value",
            tags.p("Extra information"),
        )
        html = str(result)
        assert "Extra information" in html

    def test_value_box_html_title(self) -> None:
        """Test value_box with HTML title."""
        result = value_box(
            tags.strong("Bold Title"),
            "Value",
        )
        html = str(result)
        assert "<strong>Bold Title</strong>" in html

    def test_value_box_html_value(self) -> None:
        """Test value_box with HTML value."""
        result = value_box(
            "Title",
            tags.span("$1,000", class_="currency"),
        )
        html = str(result)
        assert "currency" in html
