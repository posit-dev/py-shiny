"""Tests for shiny.ui._valuebox module showcase layouts."""

from shiny.ui._valuebox import (
    ShowcaseLayout,
    showcase_bottom,
    showcase_left_center,
    showcase_top_right,
)


class TestShowcaseLayout:
    """Tests for ShowcaseLayout dataclass."""

    def test_showcase_layout_basic(self):
        """Test creating a basic ShowcaseLayout."""
        layout = ShowcaseLayout(class_="my-showcase")

        assert layout.class_ == "my-showcase"
        assert layout.width == "33%"
        assert layout.max_height == "100px"

    def test_showcase_layout_custom_values(self):
        """Test ShowcaseLayout with custom values."""
        layout = ShowcaseLayout(
            class_="custom-showcase",
            width="50%",
            width_full_screen="2fr",
            height="200px",
            height_full_screen="50%",
            max_height="150px",
            max_height_full_screen="80%",
        )

        assert layout.class_ == "custom-showcase"
        assert layout.width == "50%"
        assert layout.width_full_screen == "2fr"
        assert layout.height == "200px"
        assert layout.height_full_screen == "50%"
        assert layout.max_height == "150px"
        assert layout.max_height_full_screen == "80%"

    def test_showcase_layout_none_values(self):
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


class TestShowcaseLeftCenter:
    """Tests for showcase_left_center function."""

    def test_showcase_left_center_default(self):
        """Test showcase_left_center with default values."""
        layout = showcase_left_center()

        assert layout.class_ == "showcase-left-center"
        assert layout.width == "30%"
        assert layout.max_height == "100px"

    def test_showcase_left_center_custom(self):
        """Test showcase_left_center with custom values."""
        layout = showcase_left_center(
            width="40%",
            max_height="150px",
        )

        assert layout.width == "40%"
        assert layout.max_height == "150px"

    def test_showcase_left_center_full_screen(self):
        """Test showcase_left_center full screen settings."""
        layout = showcase_left_center(
            width_full_screen="2fr",
            max_height_full_screen="75%",
        )

        assert layout.width_full_screen == "2fr"
        assert layout.max_height_full_screen == "75%"


class TestShowcaseTopRight:
    """Tests for showcase_top_right function."""

    def test_showcase_top_right_default(self):
        """Test showcase_top_right with default values."""
        layout = showcase_top_right()

        assert layout.class_ == "showcase-top-right"
        assert layout.width == "40%"
        assert layout.max_height == "75px"

    def test_showcase_top_right_custom(self):
        """Test showcase_top_right with custom values."""
        layout = showcase_top_right(
            width="50%",
            max_height="100px",
        )

        assert layout.width == "50%"
        assert layout.max_height == "100px"

    def test_showcase_top_right_full_screen(self):
        """Test showcase_top_right full screen settings."""
        layout = showcase_top_right(
            width_full_screen="1fr",
            max_height_full_screen="60%",
        )

        assert layout.width_full_screen == "1fr"
        assert layout.max_height_full_screen == "60%"


class TestShowcaseBottom:
    """Tests for showcase_bottom function."""

    def test_showcase_bottom_default(self):
        """Test showcase_bottom with default values."""
        layout = showcase_bottom()

        assert layout.class_ == "showcase-bottom"
        assert layout.width == "100%"
        assert layout.height == "auto"

    def test_showcase_bottom_custom(self):
        """Test showcase_bottom with custom values."""
        layout = showcase_bottom(
            height="150px",
            max_height="200px",
        )

        assert layout.height == "150px"
        assert layout.max_height == "200px"

    def test_showcase_bottom_full_screen(self):
        """Test showcase_bottom full screen settings."""
        layout = showcase_bottom(
            width_full_screen="2fr",
            height_full_screen="1fr",
        )

        assert layout.width_full_screen == "2fr"
        assert layout.height_full_screen == "1fr"
