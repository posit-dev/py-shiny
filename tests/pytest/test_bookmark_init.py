"""Tests for shiny/bookmark/__init__.py module exports."""

import shiny.bookmark as bookmark


class TestBookmarkExports:
    """Tests for bookmark module exports."""

    def test_bookmark_state_exported(self):
        """Test BookmarkState is exported."""
        assert hasattr(bookmark, "BookmarkState")

    def test_restore_state_exported(self):
        """Test RestoreState is exported."""
        assert hasattr(bookmark, "RestoreState")

    def test_bookmark_module_has_all(self):
        """Test bookmark module has __all__."""
        assert hasattr(bookmark, "__all__")


class TestBookmarkAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(bookmark.__all__, tuple)

    def test_all_contains_bookmark_state(self):
        """Test __all__ contains BookmarkState."""
        assert "BookmarkState" in bookmark.__all__

    def test_all_contains_restore_state(self):
        """Test __all__ contains RestoreState."""
        assert "RestoreState" in bookmark.__all__
