"""Tests for shiny/ui/_plot_output_opts.py - Plot output options."""

from shiny.ui._plot_output_opts import (
    brush_opts,
    click_opts,
    dblclick_opts,
    format_opt_names,
    hover_opts,
)


class TestClickOpts:
    """Tests for click_opts function."""

    def test_click_opts_defaults(self):
        """Test click_opts default values."""
        opts = click_opts()
        assert opts["clip"] is True

    def test_click_opts_clip_false(self):
        """Test click_opts with clip=False."""
        opts = click_opts(clip=False)
        assert opts["clip"] is False


class TestDblclickOpts:
    """Tests for dblclick_opts function."""

    def test_dblclick_opts_defaults(self):
        """Test dblclick_opts default values."""
        opts = dblclick_opts()
        assert opts["delay"] == 400
        assert opts["clip"] is True

    def test_dblclick_opts_custom_delay(self):
        """Test dblclick_opts with custom delay."""
        opts = dblclick_opts(delay=200)
        assert opts["delay"] == 200

    def test_dblclick_opts_custom_clip(self):
        """Test dblclick_opts with custom clip."""
        opts = dblclick_opts(clip=False)
        assert opts["clip"] is False


class TestHoverOpts:
    """Tests for hover_opts function."""

    def test_hover_opts_defaults(self):
        """Test hover_opts default values."""
        opts = hover_opts()
        assert opts["delay"] == 300
        assert opts["delayType"] == "debounce"
        assert opts["clip"] is True
        assert opts["nullOutside"] is True

    def test_hover_opts_custom_delay(self):
        """Test hover_opts with custom delay."""
        opts = hover_opts(delay=500)
        assert opts["delay"] == 500

    def test_hover_opts_throttle(self):
        """Test hover_opts with throttle delay type."""
        opts = hover_opts(delay_type="throttle")
        assert opts["delayType"] == "throttle"

    def test_hover_opts_null_outside_false(self):
        """Test hover_opts with null_outside=False."""
        opts = hover_opts(null_outside=False)
        assert opts["nullOutside"] is False


class TestBrushOpts:
    """Tests for brush_opts function."""

    def test_brush_opts_defaults(self):
        """Test brush_opts default values."""
        opts = brush_opts()
        assert opts["fill"] == "#9cf"
        assert opts["stroke"] == "#036"
        assert opts["opacity"] == 0.25
        assert opts["delay"] == 300
        assert opts["delayType"] == "debounce"
        assert opts["clip"] is True
        assert opts["direction"] == "xy"
        assert opts["resetOnNew"] is False

    def test_brush_opts_custom_colors(self):
        """Test brush_opts with custom colors."""
        opts = brush_opts(fill="#ff0000", stroke="#00ff00")
        assert opts["fill"] == "#ff0000"
        assert opts["stroke"] == "#00ff00"

    def test_brush_opts_custom_opacity(self):
        """Test brush_opts with custom opacity."""
        opts = brush_opts(opacity=0.5)
        assert opts["opacity"] == 0.5

    def test_brush_opts_direction_x(self):
        """Test brush_opts with x direction only."""
        opts = brush_opts(direction="x")
        assert opts["direction"] == "x"

    def test_brush_opts_direction_y(self):
        """Test brush_opts with y direction only."""
        opts = brush_opts(direction="y")
        assert opts["direction"] == "y"

    def test_brush_opts_reset_on_new(self):
        """Test brush_opts with reset_on_new=True."""
        opts = brush_opts(reset_on_new=True)
        assert opts["resetOnNew"] is True

    def test_brush_opts_throttle(self):
        """Test brush_opts with throttle delay type."""
        opts = brush_opts(delay_type="throttle")
        assert opts["delayType"] == "throttle"


class TestFormatOptNames:
    """Tests for format_opt_names function."""

    def test_format_opt_names_click(self):
        """Test format_opt_names with click opts."""
        opts = click_opts()
        formatted = format_opt_names(opts, "click")
        assert "data-click-clip" in formatted
        assert formatted["data-click-clip"] == "true"

    def test_format_opt_names_converts_camel_to_kebab(self):
        """Test that camelCase is converted to kebab-case."""
        opts = hover_opts()
        formatted = format_opt_names(opts, "hover")
        assert "data-hover-delay-type" in formatted
        assert "data-hover-null-outside" in formatted

    def test_format_opt_names_bool_values_lowercase(self):
        """Test that boolean values are lowercase strings."""
        opts = click_opts(clip=True)
        formatted = format_opt_names(opts, "click")
        assert formatted["data-click-clip"] == "true"

        opts = click_opts(clip=False)
        formatted = format_opt_names(opts, "click")
        assert formatted["data-click-clip"] == "false"

    def test_format_opt_names_numeric_values(self):
        """Test that numeric values are converted to strings."""
        opts = dblclick_opts(delay=400)
        formatted = format_opt_names(opts, "dblclick")
        assert formatted["data-dblclick-delay"] == "400"

    def test_format_opt_names_brush(self):
        """Test format_opt_names with brush opts."""
        opts = brush_opts()
        formatted = format_opt_names(opts, "brush")
        assert "data-brush-fill" in formatted
        assert "data-brush-stroke" in formatted
        assert "data-brush-opacity" in formatted
        assert "data-brush-delay" in formatted
        assert "data-brush-delay-type" in formatted
        assert "data-brush-clip" in formatted
        assert "data-brush-direction" in formatted
        assert "data-brush-reset-on-new" in formatted
