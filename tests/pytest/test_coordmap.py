"""Tests for shiny/render/_coordmap.py module."""

from shiny.render._coordmap import get_coordmap


class TestGetCoordmap:
    """Tests for get_coordmap function."""

    def test_get_coordmap_is_callable(self):
        """Test get_coordmap is callable."""
        assert callable(get_coordmap)
