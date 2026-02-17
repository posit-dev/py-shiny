"""Tests for shiny/ui/_plot_output_opts.py module."""


class TestPlotOutputOpts:
    """Tests for plot output opts module."""

    def test_module_exists(self):
        """Test plot output opts module can be imported."""
        from shiny.ui import _plot_output_opts

        assert _plot_output_opts is not None

    def test_brush_opts_function_exists(self):
        """Test brush_opts exists."""
        from shiny.ui._plot_output_opts import brush_opts

        assert callable(brush_opts)

    def test_click_opts_function_exists(self):
        """Test click_opts exists."""
        from shiny.ui._plot_output_opts import click_opts

        assert callable(click_opts)

    def test_dblclick_opts_function_exists(self):
        """Test dblclick_opts exists."""
        from shiny.ui._plot_output_opts import dblclick_opts

        assert callable(dblclick_opts)

    def test_hover_opts_function_exists(self):
        """Test hover_opts exists."""
        from shiny.ui._plot_output_opts import hover_opts

        assert callable(hover_opts)


class TestPlotOptsExported:
    """Tests for plot opts functions export."""

    def test_brush_opts_in_ui(self):
        """Test brush_opts is in ui module."""
        from shiny import ui

        assert hasattr(ui, "brush_opts")

    def test_click_opts_in_ui(self):
        """Test click_opts is in ui module."""
        from shiny import ui

        assert hasattr(ui, "click_opts")

    def test_hover_opts_in_ui(self):
        """Test hover_opts is in ui module."""
        from shiny import ui

        assert hasattr(ui, "hover_opts")
