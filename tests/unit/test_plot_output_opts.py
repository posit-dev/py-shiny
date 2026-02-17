"""Tests for shiny/ui/_plot_output_opts.py"""

from shiny.ui._plot_output_opts import (
    ClickOpts,
    HoverOpts,
    brush_opts,
    click_opts,
    dblclick_opts,
    format_opt_names,
    hover_opts,
)


class TestClickOpts:
    """Tests for the click_opts function."""

    def test_click_opts_default(self):
        """Test click_opts with default values."""
        result = click_opts()
        assert isinstance(result, dict)
        assert result["clip"] is True

    def test_click_opts_clip_false(self):
        """Test click_opts with clip=False."""
        result = click_opts(clip=False)
        assert result["clip"] is False


class TestDblclickOpts:
    """Tests for the dblclick_opts function."""

    def test_dblclick_opts_default(self):
        """Test dblclick_opts with default values."""
        result = dblclick_opts()
        assert isinstance(result, dict)
        assert result["delay"] == 400
        assert result["clip"] is True

    def test_dblclick_opts_custom_delay(self):
        """Test dblclick_opts with custom delay."""
        result = dblclick_opts(delay=500)
        assert result["delay"] == 500

    def test_dblclick_opts_clip_false(self):
        """Test dblclick_opts with clip=False."""
        result = dblclick_opts(clip=False)
        assert result["clip"] is False


class TestHoverOpts:
    """Tests for the hover_opts function."""

    def test_hover_opts_default(self):
        """Test hover_opts with default values."""
        result = hover_opts()
        assert isinstance(result, dict)
        assert result["delay"] == 300
        assert result["delayType"] == "debounce"
        assert result["clip"] is True
        assert result["nullOutside"] is True

    def test_hover_opts_custom_delay(self):
        """Test hover_opts with custom delay."""
        result = hover_opts(delay=500)
        assert result["delay"] == 500

    def test_hover_opts_throttle(self):
        """Test hover_opts with delay_type=throttle."""
        result = hover_opts(delay_type="throttle")
        assert result["delayType"] == "throttle"

    def test_hover_opts_clip_false(self):
        """Test hover_opts with clip=False."""
        result = hover_opts(clip=False)
        assert result["clip"] is False

    def test_hover_opts_null_outside_false(self):
        """Test hover_opts with null_outside=False."""
        result = hover_opts(null_outside=False)
        assert result["nullOutside"] is False


class TestBrushOpts:
    """Tests for the brush_opts function."""

    def test_brush_opts_default(self):
        """Test brush_opts with default values."""
        result = brush_opts()
        assert isinstance(result, dict)
        assert result["fill"] == "#9cf"
        assert result["stroke"] == "#036"
        assert result["opacity"] == 0.25
        assert result["delay"] == 300
        assert result["delayType"] == "debounce"
        assert result["clip"] is True
        assert result["direction"] == "xy"
        assert result["resetOnNew"] is False

    def test_brush_opts_custom_colors(self):
        """Test brush_opts with custom fill and stroke."""
        result = brush_opts(fill="#ff0000", stroke="#0000ff")
        assert result["fill"] == "#ff0000"
        assert result["stroke"] == "#0000ff"

    def test_brush_opts_custom_opacity(self):
        """Test brush_opts with custom opacity."""
        result = brush_opts(opacity=0.5)
        assert result["opacity"] == 0.5

    def test_brush_opts_custom_delay(self):
        """Test brush_opts with custom delay."""
        result = brush_opts(delay=500)
        assert result["delay"] == 500

    def test_brush_opts_throttle(self):
        """Test brush_opts with delay_type=throttle."""
        result = brush_opts(delay_type="throttle")
        assert result["delayType"] == "throttle"

    def test_brush_opts_direction_x(self):
        """Test brush_opts with direction=x."""
        result = brush_opts(direction="x")
        assert result["direction"] == "x"

    def test_brush_opts_direction_y(self):
        """Test brush_opts with direction=y."""
        result = brush_opts(direction="y")
        assert result["direction"] == "y"

    def test_brush_opts_reset_on_new_true(self):
        """Test brush_opts with reset_on_new=True."""
        result = brush_opts(reset_on_new=True)
        assert result["resetOnNew"] is True


class TestFormatOptNames:
    """Tests for the format_opt_names function."""

    def test_format_opt_names_click(self):
        """Test format_opt_names with click opts."""
        opts: ClickOpts = {"clip": True}
        result = format_opt_names(opts, "click")
        assert "data-click-clip" in result
        assert result["data-click-clip"] == "true"

    def test_format_opt_names_hover(self):
        """Test format_opt_names with hover opts."""
        opts: HoverOpts = {
            "delay": 300,
            "delayType": "debounce",
            "clip": True,
            "nullOutside": True,
        }
        result = format_opt_names(opts, "hover")
        assert "data-hover-delay" in result
        assert "data-hover-delay-type" in result
        assert "data-hover-clip" in result
        assert "data-hover-null-outside" in result

    def test_format_opt_names_boolean_lowercase(self):
        """Test format_opt_names converts boolean to lowercase string."""
        opts: ClickOpts = {"clip": False}
        result = format_opt_names(opts, "test")
        assert result["data-test-clip"] == "false"

    def test_format_opt_names_camel_to_kebab(self):
        """Test format_opt_names converts camelCase to kebab-case."""
        opts: HoverOpts = {
            "delay": 300,
            "delayType": "throttle",
            "clip": True,
            "nullOutside": False,
        }
        result = format_opt_names(opts, "test")
        # delayType -> delay-type
        assert "data-test-delay-type" in result
        # nullOutside -> null-outside
        assert "data-test-null-outside" in result
