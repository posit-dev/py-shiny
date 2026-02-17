"""Tests for shiny.ui.value_box module."""

from htmltools import Tag

from shiny.ui import value_box


class TestValueBox:
    """Tests for value_box function."""

    def test_value_box_basic(self) -> None:
        """Test basic value_box creation."""
        result = value_box("Title", "100")
        assert isinstance(result, Tag)

    def test_value_box_with_title(self) -> None:
        """Test value_box with title."""
        result = value_box("Total Sales", "$1,000")
        html = str(result)
        assert "Total Sales" in html

    def test_value_box_with_value(self) -> None:
        """Test value_box with value."""
        result = value_box("Metric", "42")
        html = str(result)
        assert "42" in html

    def test_value_box_with_showcase(self) -> None:
        """Test value_box with showcase parameter."""
        from htmltools import div

        result = value_box("Title", "100", showcase=div("Icon"))
        html = str(result)
        assert "Icon" in html

    def test_value_box_showcase_layout_left_center(self) -> None:
        """Test value_box with showcase_layout parameter."""
        result = value_box("Title", "100", showcase_layout="left center")
        html = str(result)
        assert "Title" in html

    def test_value_box_showcase_layout_top_right(self) -> None:
        """Test value_box with showcase_layout='top right'."""
        result = value_box("Title", "100", showcase_layout="top right")
        html = str(result)
        assert "Title" in html

    def test_value_box_showcase_layout_bottom(self) -> None:
        """Test value_box with showcase_layout='bottom'."""
        result = value_box("Title", "100", showcase_layout="bottom")
        html = str(result)
        assert "Title" in html

    def test_value_box_with_full_screen(self) -> None:
        """Test value_box with full_screen parameter."""
        result = value_box("Title", "100", full_screen=True)
        html = str(result)
        assert "Title" in html

    def test_value_box_with_theme(self) -> None:
        """Test value_box with theme parameter."""
        result = value_box("Title", "100", theme="primary")
        html = str(result)
        assert "Title" in html

    def test_value_box_with_height(self) -> None:
        """Test value_box with height parameter."""
        result = value_box("Title", "100", height="200px")
        html = str(result)
        assert "Title" in html

    def test_value_box_with_max_height(self) -> None:
        """Test value_box with max_height parameter."""
        result = value_box("Title", "100", max_height="300px")
        html = str(result)
        assert "Title" in html

    def test_value_box_with_class(self) -> None:
        """Test value_box with class_ parameter."""
        result = value_box("Title", "100", class_="my-class")
        html = str(result)
        assert "my-class" in html

    def test_value_box_has_value_box_class(self) -> None:
        """Test value_box has value-box class."""
        result = value_box("Title", "100")
        html = str(result)
        assert "value-box" in html or "bslib" in html

    def test_value_box_with_multiple_values(self) -> None:
        """Test value_box displays correctly."""
        result = value_box("Revenue", "$12,345")
        html = str(result)
        assert "Revenue" in html
        assert "$12,345" in html
