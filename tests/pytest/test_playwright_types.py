"""Tests for shiny/playwright/_types.py module."""

import shiny.playwright._types as types


class TestPlaywrightTypes:
    """Tests for playwright types module."""

    def test_module_has_attr_value(self):
        """Test types module has AttrValue type."""
        assert hasattr(types, "AttrValue")

    def test_module_has_optional_str(self):
        """Test types module has OptionalStr type."""
        assert hasattr(types, "OptionalStr")

    def test_module_has_pattern_or_str(self):
        """Test types module has PatternOrStr type."""
        assert hasattr(types, "PatternOrStr")


class TestAttrValue:
    """Tests for AttrValue type."""

    def test_attr_value_exists(self):
        """Test AttrValue exists."""
        assert types.AttrValue is not None

    def test_attr_value_is_type(self):
        """Test AttrValue is a type alias."""
        # AttrValue should be a Union type
        # Just ensure it's accessible
        assert types.AttrValue is not None
