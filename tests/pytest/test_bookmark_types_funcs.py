"""Tests for shiny.bookmark._types module"""

from pathlib import Path

from shiny.bookmark._types import (
    BookmarkDirFn,
    BookmarkDirFnAsync,
    BookmarkRestoreDirFn,
    BookmarkSaveDirFn,
    BookmarkStore,
)


class TestBookmarkStoreType:
    """Test BookmarkStore literal type"""

    def test_url_value(self):
        """Test 'url' is a valid BookmarkStore value"""
        store: BookmarkStore = "url"
        assert store == "url"

    def test_server_value(self):
        """Test 'server' is a valid BookmarkStore value"""
        store: BookmarkStore = "server"
        assert store == "server"

    def test_disable_value(self):
        """Test 'disable' is a valid BookmarkStore value"""
        store: BookmarkStore = "disable"
        assert store == "disable"


class TestBookmarkDirFnType:
    """Test bookmark directory function types"""

    def test_sync_function(self):
        """Test sync function satisfies BookmarkDirFn"""

        def sync_fn(bookmark_id: str) -> Path:
            return Path(f"/tmp/{bookmark_id}")

        # This should type-check as BookmarkDirFn
        fn: BookmarkDirFn = sync_fn
        result = fn("test123")
        # Result could be Path or Awaitable[Path]
        assert result == Path("/tmp/test123")

    def test_async_function_signature(self):
        """Test async function can satisfy BookmarkDirFnAsync"""
        import asyncio

        async def async_fn(bookmark_id: str) -> Path:
            return Path(f"/tmp/bookmarks/{bookmark_id}")

        # This should type-check as BookmarkDirFnAsync
        fn: BookmarkDirFnAsync = async_fn
        # Run the async function
        result = asyncio.run(fn("bookmark_abc"))
        assert result == Path("/tmp/bookmarks/bookmark_abc")

    def test_save_dir_fn_type(self):
        """Test BookmarkSaveDirFn type"""
        import asyncio

        async def save_fn(bookmark_id: str) -> Path:
            return Path(f"/save/{bookmark_id}")

        fn: BookmarkSaveDirFn = save_fn
        result = asyncio.run(fn("save_123"))
        assert result == Path("/save/save_123")

    def test_restore_dir_fn_type(self):
        """Test BookmarkRestoreDirFn type"""
        import asyncio

        async def restore_fn(bookmark_id: str) -> Path:
            return Path(f"/restore/{bookmark_id}")

        fn: BookmarkRestoreDirFn = restore_fn
        result = asyncio.run(fn("restore_456"))
        assert result == Path("/restore/restore_456")


class TestBookmarkDirFnUsage:
    """Test practical usage of bookmark directory functions"""

    def test_path_construction(self):
        """Test that functions return proper Path objects"""

        def get_bookmark_dir(bookmark_id: str) -> Path:
            base = Path("/var/shiny/bookmarks")
            return base / bookmark_id

        fn: BookmarkDirFn = get_bookmark_dir
        result = fn("my_bookmark")
        assert isinstance(result, Path)
        assert str(result) == "/var/shiny/bookmarks/my_bookmark"

    def test_path_with_subdirectory(self):
        """Test bookmark path with nested structure"""

        def get_nested_dir(bookmark_id: str) -> Path:
            prefix = bookmark_id[:2]
            return Path(f"/bookmarks/{prefix}/{bookmark_id}")

        fn: BookmarkDirFn = get_nested_dir
        result = fn("abcdef123")
        assert result == Path("/bookmarks/ab/abcdef123")
