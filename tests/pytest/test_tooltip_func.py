import json

import pytest
from htmltools import tags

from shiny.ui._tooltip import tooltip


class TestTooltip:
    """Tests for the tooltip function."""

    def test_tooltip_basic(self):
        """Test basic tooltip creation with trigger and content."""
        result = tooltip(
            tags.button("Hover me"),
            "Tooltip text",
        )

        assert result.name == "bslib-tooltip"
        result_str = str(result)
        assert "Tooltip text" in result_str
        assert "Hover me" in result_str

    def test_tooltip_with_id(self):
        """Test tooltip with explicit id."""
        result = tooltip(
            tags.button("Trigger"),
            "Content",
            id="my_tooltip",
        )

        assert result.attrs.get("id") == "my_tooltip"

    def test_tooltip_placement_auto(self):
        """Test tooltip with auto placement."""
        result = tooltip(
            tags.button("Trigger"),
            "Content",
            placement="auto",
        )
        assert result.attrs.get("placement") == "auto"

    def test_tooltip_placement_top(self):
        """Test tooltip with top placement."""
        result = tooltip(
            tags.button("Trigger"),
            "Content",
            placement="top",
        )
        assert result.attrs.get("placement") == "top"

    def test_tooltip_placement_right(self):
        """Test tooltip with right placement."""
        result = tooltip(
            tags.button("Trigger"),
            "Content",
            placement="right",
        )
        assert result.attrs.get("placement") == "right"

    def test_tooltip_placement_bottom(self):
        """Test tooltip with bottom placement."""
        result = tooltip(
            tags.button("Trigger"),
            "Content",
            placement="bottom",
        )
        assert result.attrs.get("placement") == "bottom"

    def test_tooltip_placement_left(self):
        """Test tooltip with left placement."""
        result = tooltip(
            tags.button("Trigger"),
            "Content",
            placement="left",
        )
        assert result.attrs.get("placement") == "left"

    def test_tooltip_with_options(self):
        """Test tooltip with additional options."""
        result = tooltip(
            tags.button("Trigger"),
            "Content",
            options={"delay": {"show": 100, "hide": 200}},
        )

        bs_options = result.attrs.get("bsOptions")
        assert bs_options is not None
        options_dict = json.loads(str(bs_options))
        assert options_dict.get("delay") == {"show": 100, "hide": 200}

    def test_tooltip_no_content_raises_error(self):
        """Test that tooltip raises error when no content is provided."""
        with pytest.raises(RuntimeError, match="At least one value"):
            tooltip(tags.button("Trigger"))

    def test_tooltip_multiple_content_items(self):
        """Test tooltip with multiple content items."""
        result = tooltip(
            tags.button("Trigger"),
            "First part",
            tags.span("Second part"),
        )

        result_str = str(result)
        assert "First part" in result_str
        assert "Second part" in result_str

    def test_tooltip_with_kwargs(self):
        """Test tooltip with additional HTML attributes."""
        result = tooltip(
            tags.button("Trigger"),
            "Content",
            class_="custom-tooltip",
        )

        result_str = str(result)
        assert "bslib-tooltip" in result_str

    def test_tooltip_none_options(self):
        """Test tooltip with None options (default)."""
        result = tooltip(
            tags.button("Trigger"),
            "Content",
            options=None,
        )

        # bsOptions should be None or not present
        bs_options = result.attrs.get("bsOptions")
        assert bs_options is None

    def test_tooltip_with_complex_trigger(self):
        """Test tooltip with complex trigger element."""
        trigger = tags.a(
            tags.span("Link text"),
            href="#",
            class_="btn",
        )

        result = tooltip(
            trigger,
            "Tooltip content",
        )

        result_str = str(result)
        assert "Link text" in result_str

    def test_tooltip_returns_tag(self):
        """Test that tooltip returns a Tag object."""
        result = tooltip(
            tags.button("Trigger"),
            "Content",
        )

        from htmltools import Tag

        assert isinstance(result, Tag)

    def test_tooltip_with_span_trigger(self):
        """Test tooltip with span trigger (non-focusable element)."""
        result = tooltip(
            tags.span("Info icon"),
            "Information tooltip",
        )

        result_str = str(result)
        assert "Info icon" in result_str
        assert "Information tooltip" in result_str

    def test_tooltip_with_html_content(self):
        """Test tooltip with HTML content."""
        result = tooltip(
            tags.button("Trigger"),
            tags.strong("Bold"),
            " and ",
            tags.em("italic"),
        )

        result_str = str(result)
        assert "strong" in result_str
        assert "em" in result_str
