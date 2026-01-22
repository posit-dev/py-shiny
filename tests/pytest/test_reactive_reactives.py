"""Tests for shiny/reactive/_reactives.py module."""

from shiny.reactive._reactives import (
    value,
    Value,
)


class TestReactiveValue:
    """Tests for reactive.value function."""

    def test_value_is_callable(self):
        """Test value is callable."""
        assert callable(value)

    def test_value_returns_reactive_value(self):
        """Test value returns Value object."""
        result = value(0)
        assert isinstance(result, Value)


class TestValueClass:
    """Tests for Value class."""

    def test_value_class_exists(self):
        """Test Value class exists."""
        assert Value is not None

    def test_value_is_type(self):
        """Test Value is a class."""
        assert isinstance(Value, type)

    def test_value_can_be_instantiated(self):
        """Test Value can be created."""
        v = Value(42)
        assert v is not None


class TestReactiveExported:
    """Tests for reactive functions export."""

    def test_value_in_reactive(self):
        """Test value is in reactive module."""
        from shiny import reactive

        assert hasattr(reactive, "value")

    def test_value_class_in_reactive(self):
        """Test Value is in reactive module."""
        from shiny import reactive

        assert hasattr(reactive, "Value")
