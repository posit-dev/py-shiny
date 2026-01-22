"""Tests for shiny/playwright/controller/__init__.py module."""

import shiny.playwright.controller as controller


class TestControllerExports:
    """Tests for controller module exports."""

    def test_controller_has_input_action_button(self):
        """Test controller has InputActionButton."""
        assert hasattr(controller, "InputActionButton")

    def test_controller_has_input_select(self):
        """Test controller has InputSelect."""
        assert hasattr(controller, "InputSelect")

    def test_controller_has_output_text(self):
        """Test controller has OutputText."""
        assert hasattr(controller, "OutputText")


class TestControllerAll:
    """Tests for __all__ exports."""

    def test_all_is_list(self):
        """Test __all__ is a list."""
        assert isinstance(controller.__all__, list)

    def test_all_contains_input_action_button(self):
        """Test __all__ contains InputActionButton."""
        assert "InputActionButton" in controller.__all__

    def test_all_contains_input_text(self):
        """Test __all__ contains InputText."""
        assert "InputText" in controller.__all__

    def test_all_contains_output_text(self):
        """Test __all__ contains OutputText."""
        assert "OutputText" in controller.__all__

    def test_all_contains_output_plot(self):
        """Test __all__ contains OutputPlot."""
        assert "OutputPlot" in controller.__all__

    def test_all_contains_sidebar(self):
        """Test __all__ contains Sidebar."""
        assert "Sidebar" in controller.__all__
