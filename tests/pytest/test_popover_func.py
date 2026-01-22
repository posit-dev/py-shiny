import json
from typing import Literal

import pytest
from htmltools import tags

from shiny.ui._popover import popover

PlacementType = Literal["auto", "top", "right", "bottom", "left"]


class TestPopover:
    """Tests for the popover function."""

    def test_popover_basic(self):
        """Test basic popover creation with trigger and content."""
        result = popover(
            tags.button("Click me", id="trigger_btn"),
            "Popover content",
        )

        assert result.name == "bslib-popover"
        result_str = str(result)
        assert "Popover content" in result_str
        assert "Click me" in result_str

    def test_popover_with_title(self):
        """Test popover with title."""
        result = popover(
            tags.button("Trigger"),
            "Body content",
            title="Popover Title",
        )

        result_str = str(result)
        assert "bslib-popover" in result_str
        assert "Popover Title" in result_str
        assert "Body content" in result_str

    def test_popover_with_id(self):
        """Test popover with explicit id."""
        result = popover(
            tags.button("Trigger"),
            "Content",
            id="my_popover",
        )

        assert result.attrs.get("id") == "my_popover"

    def test_popover_placement_auto(self):
        """Test popover with auto placement."""
        result = popover(
            tags.button("Trigger"),
            "Content",
            placement="auto",
        )
        assert result.attrs.get("placement") == "auto"

    def test_popover_placement_top(self):
        """Test popover with top placement."""
        result = popover(
            tags.button("Trigger"),
            "Content",
            placement="top",
        )
        assert result.attrs.get("placement") == "top"

    def test_popover_placement_right(self):
        """Test popover with right placement."""
        result = popover(
            tags.button("Trigger"),
            "Content",
            placement="right",
        )
        assert result.attrs.get("placement") == "right"

    def test_popover_placement_bottom(self):
        """Test popover with bottom placement."""
        result = popover(
            tags.button("Trigger"),
            "Content",
            placement="bottom",
        )
        assert result.attrs.get("placement") == "bottom"

    def test_popover_placement_left(self):
        """Test popover with left placement."""
        result = popover(
            tags.button("Trigger"),
            "Content",
            placement="left",
        )
        assert result.attrs.get("placement") == "left"

    def test_popover_with_options(self):
        """Test popover with additional options."""
        result = popover(
            tags.button("Trigger"),
            "Content",
            options={"trigger": "hover"},
        )

        bs_options = result.attrs.get("bsOptions")
        assert bs_options is not None
        options_dict = json.loads(str(bs_options))
        assert options_dict.get("trigger") == "hover"

    def test_popover_no_content_raises_error(self):
        """Test that popover raises error when no content is provided."""
        with pytest.raises(RuntimeError, match="At least one value"):
            popover(tags.button("Trigger"))

    def test_popover_forbidden_option_content(self):
        """Test that content option in options raises error."""
        with pytest.raises(RuntimeError, match="content"):
            popover(
                tags.button("Trigger"),
                "Body",
                options={"content": "Not allowed"},
            )

    def test_popover_forbidden_option_title(self):
        """Test that title option in options raises error."""
        with pytest.raises(RuntimeError, match="title"):
            popover(
                tags.button("Trigger"),
                "Body",
                options={"title": "Not allowed"},
            )

    def test_popover_forbidden_option_placement(self):
        """Test that placement option in options raises error."""
        with pytest.raises(RuntimeError, match="placement"):
            popover(
                tags.button("Trigger"),
                "Body",
                options={"placement": "top"},
            )

    def test_popover_multiple_content_items(self):
        """Test popover with multiple content items."""
        result = popover(
            tags.button("Trigger"),
            "First paragraph",
            tags.p("Second paragraph"),
            tags.div("Third content"),
        )

        result_str = str(result)
        assert "First paragraph" in result_str
        assert "Second paragraph" in result_str
        assert "Third content" in result_str

    def test_popover_with_kwargs(self):
        """Test popover with additional HTML attributes."""
        result = popover(
            tags.button("Trigger"),
            "Content",
            class_="custom-class",
            data_custom="value",
        )

        # The kwargs should be passed to consolidate_attrs
        result_str = str(result)
        assert "bslib-popover" in result_str

    def test_popover_empty_options(self):
        """Test popover with empty options dictionary."""
        result = popover(
            tags.button("Trigger"),
            "Content",
            options={},
        )

        # Empty options should serialize to empty JSON object
        bs_options = result.attrs.get("bsOptions")
        assert bs_options == "{}"

    def test_popover_with_complex_trigger(self):
        """Test popover with complex trigger element."""
        trigger = tags.div(
            tags.span("Icon"),
            tags.span("Label"),
            class_="btn btn-primary",
        )

        result = popover(
            trigger,
            "Popover content",
        )

        result_str = str(result)
        assert "Icon" in result_str
        assert "Label" in result_str

    def test_popover_with_html_content(self):
        """Test popover with HTML content."""
        result = popover(
            tags.button("Trigger"),
            tags.strong("Bold text"),
            tags.em("Italic text"),
        )

        result_str = str(result)
        assert "strong" in result_str
        assert "Bold text" in result_str
