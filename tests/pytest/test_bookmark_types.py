"""Tests for shiny/bookmark/_types.py module."""

from shiny.bookmark._types import BookmarkStore


class TestBookmarkStore:
    """Tests for BookmarkStore type."""

    def test_bookmark_store_exists(self):
        """Test BookmarkStore exists."""
        assert BookmarkStore is not None


class TestBookmarkDirFn:
    """Tests for BookmarkDirFn type."""

    def test_bookmark_dir_fn_importable(self):
        """Test BookmarkDirFn is importable from shiny.bookmark._types."""
        from shiny.bookmark._types import BookmarkDirFn

        assert BookmarkDirFn is not None
