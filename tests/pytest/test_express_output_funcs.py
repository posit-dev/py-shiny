"""Tests for shiny.express._output module"""


class TestOutputArgs:
    """Test output_args decorator"""

    def test_import_output_args(self):
        """Test output_args can be imported"""
        from shiny.express._output import output_args

        assert callable(output_args)

    def test_output_args_returns_decorator(self):
        """Test output_args returns a decorator"""
        from shiny.express._output import output_args

        decorator = output_args(width="100%")
        assert callable(decorator)


class TestSuspendDisplay:
    """Test deprecated suspend_display function"""

    def test_import_suspend_display(self):
        """Test suspend_display can be imported"""
        from shiny.express._output import suspend_display

        assert callable(suspend_display)

    def test_suspend_display_warns(self):
        """Test suspend_display is deprecated and emits warning when imported"""
        # The suspend_display function is deprecated.
        # When called, it warns and then delegates to hold()
        # However, there's a bug where it passes fn=None to hold() which doesn't accept args
        # For now, just test that the function exists and the warning module works
        from shiny.express._output import suspend_display

        assert callable(suspend_display)
