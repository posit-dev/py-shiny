"""Tests for shiny/reactive/_extended_task.py module."""

from shiny.reactive._extended_task import (
    ExtendedTask,
)


class TestExtendedTask:
    """Tests for ExtendedTask class."""

    def test_extended_task_class_exists(self):
        """Test ExtendedTask class exists."""
        assert ExtendedTask is not None

    def test_extended_task_is_type(self):
        """Test ExtendedTask is a class."""
        assert isinstance(ExtendedTask, type)


class TestExtendedTaskExported:
    """Tests for extended task export."""

    def test_extended_task_in_reactive(self):
        """Test ExtendedTask is in reactive module."""
        from shiny import reactive

        assert hasattr(reactive, "ExtendedTask")
