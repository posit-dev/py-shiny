"""Tests for value box UI components."""

from htmltools import tags

from shiny.ui import (
    showcase_bottom,
    showcase_left_center,
    showcase_top_right,
    value_box,
    value_box_theme,
)


class TestValueBox:
    """Tests for value_box function."""

    def test_basic_value_box(self):
        """Test creating a basic value box."""
        vb = value_box(
            title="Total Sales",
            value="$1,234",
        )
        html = str(vb)

        assert "Total Sales" in html
        assert "$1,234" in html

    def test_value_box_with_showcase(self):
        """Test value box with showcase content."""
        vb = value_box(
            title="Users",
            value="1,000",
            showcase=tags.i(class_="fa fa-users"),
        )
        html = str(vb)

        assert "Users" in html
        assert "1,000" in html

    def test_value_box_with_theme(self):
        """Test value box with a theme."""
        vb = value_box(
            title="Revenue",
            value="$500",
            theme="primary",
        )
        html = str(vb)

        assert "Revenue" in html
        assert "$500" in html

    def test_value_box_full_screen(self):
        """Test value box with full screen option."""
        vb = value_box(
            title="Metric",
            value="42",
            full_screen=True,
        )
        html = str(vb)

        assert "Metric" in html
        assert "42" in html

    def test_value_box_with_height(self):
        """Test value box with explicit height."""
        vb = value_box(
            title="Count",
            value="100",
            height="200px",
        )
        html = str(vb)

        assert "Count" in html


class TestShowcaseLayouts:
    """Tests for showcase layout functions."""

    def test_showcase_left_center(self):
        """Test showcase_left_center layout."""
        layout = showcase_left_center()
        assert layout is not None
        assert layout.class_ == "showcase-left-center"

    def test_showcase_left_center_with_width(self):
        """Test showcase_left_center with custom width."""
        layout = showcase_left_center(width="50%")
        assert layout.width == "50%"

    def test_showcase_top_right(self):
        """Test showcase_top_right layout."""
        layout = showcase_top_right()
        assert layout is not None
        assert layout.class_ == "showcase-top-right"

    def test_showcase_top_right_with_dimensions(self):
        """Test showcase_top_right with custom dimensions."""
        layout = showcase_top_right(width="40%", max_height="100px")
        assert layout.width == "40%"
        assert layout.max_height == "100px"

    def test_showcase_bottom(self):
        """Test showcase_bottom layout."""
        layout = showcase_bottom()
        assert layout is not None
        assert layout.class_ == "showcase-bottom"


class TestValueBoxTheme:
    """Tests for value_box_theme function."""

    def test_basic_value_box_theme(self):
        """Test creating a basic value box theme."""
        theme = value_box_theme("primary")
        assert theme is not None
        assert theme.class_ is not None
        assert "primary" in str(theme.class_)

    def test_value_box_theme_with_fg_bg(self):
        """Test value box theme with foreground/background."""
        theme = value_box_theme(fg="#ffffff", bg="#000000")
        assert theme is not None
