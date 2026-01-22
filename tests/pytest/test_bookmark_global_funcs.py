"""Tests for shiny.bookmark._global module"""

from pathlib import Path

import pytest

from shiny.bookmark._global import (
    as_bookmark_dir_fn,
    get_bookmark_restore_dir_fn,
    get_bookmark_save_dir_fn,
    set_global_restore_dir_fn,
    set_global_save_dir_fn,
)
from shiny.types import MISSING


class TestAsBookmarkDirFn:
    """Test as_bookmark_dir_fn function"""

    def test_as_bookmark_dir_fn_none(self):
        """Test as_bookmark_dir_fn with None"""
        result = as_bookmark_dir_fn(None)
        assert result is None

    def test_as_bookmark_dir_fn_sync(self):
        """Test as_bookmark_dir_fn with sync function"""

        def sync_fn(id: str) -> Path:
            return Path(f"/tmp/{id}")

        result = as_bookmark_dir_fn(sync_fn)
        # Result should be an async-wrapped function
        assert callable(result)

    @pytest.mark.asyncio
    async def test_as_bookmark_dir_fn_async(self):
        """Test as_bookmark_dir_fn with async function"""

        async def async_fn(id: str) -> Path:
            return Path(f"/tmp/{id}")

        result = as_bookmark_dir_fn(async_fn)
        # Result should be callable
        assert callable(result)
        # Result should return Path when awaited
        path = await result("test_id")
        assert path == Path("/tmp/test_id")


class TestGetBookmarkDirFns:
    """Test get_bookmark_save_dir_fn and get_bookmark_restore_dir_fn"""

    def test_get_save_dir_fn_with_missing(self):
        """Test get_bookmark_save_dir_fn with MISSING uses default"""
        # Note: This tests that MISSING_TYPE triggers default lookup
        result = get_bookmark_save_dir_fn(MISSING)
        # Result could be None or the global default
        assert result is None or callable(result)

    def test_get_save_dir_fn_with_none(self):
        """Test get_bookmark_save_dir_fn with None"""
        result = get_bookmark_save_dir_fn(None)
        assert result is None

    def test_get_save_dir_fn_with_function(self):
        """Test get_bookmark_save_dir_fn with actual function"""

        async def custom_fn(id: str) -> Path:
            return Path(f"/custom/{id}")

        result = get_bookmark_save_dir_fn(custom_fn)
        assert result is custom_fn

    def test_get_restore_dir_fn_with_missing(self):
        """Test get_bookmark_restore_dir_fn with MISSING uses default"""
        result = get_bookmark_restore_dir_fn(MISSING)
        # Result could be None or the global default
        assert result is None or callable(result)

    def test_get_restore_dir_fn_with_none(self):
        """Test get_bookmark_restore_dir_fn with None"""
        result = get_bookmark_restore_dir_fn(None)
        assert result is None

    def test_get_restore_dir_fn_with_function(self):
        """Test get_bookmark_restore_dir_fn with actual function"""

        async def custom_fn(id: str) -> Path:
            return Path(f"/restore/{id}")

        result = get_bookmark_restore_dir_fn(custom_fn)
        assert result is custom_fn


class TestSetGlobalDirFns:
    """Test set_global_save_dir_fn and set_global_restore_dir_fn"""

    def test_set_global_save_dir_fn(self):
        """Test set_global_save_dir_fn sets the function"""

        def save_fn(id: str) -> Path:
            return Path(f"/save/{id}")

        result = set_global_save_dir_fn(save_fn)
        # Should return the original function
        assert result is save_fn

    def test_set_global_restore_dir_fn(self):
        """Test set_global_restore_dir_fn sets the function"""

        def restore_fn(id: str) -> Path:
            return Path(f"/restore/{id}")

        result = set_global_restore_dir_fn(restore_fn)
        # Should return the original function
        assert result is restore_fn

    def test_set_global_save_dir_fn_affects_get(self):
        """Test set_global_save_dir_fn affects get_bookmark_save_dir_fn"""

        def custom_save(id: str) -> Path:
            return Path(f"/custom_save/{id}")

        set_global_save_dir_fn(custom_save)
        result = get_bookmark_save_dir_fn(MISSING)
        # Result should be the async-wrapped version
        assert result is not None
        assert callable(result)

    def test_set_global_restore_dir_fn_affects_get(self):
        """Test set_global_restore_dir_fn affects get_bookmark_restore_dir_fn"""

        def custom_restore(id: str) -> Path:
            return Path(f"/custom_restore/{id}")

        set_global_restore_dir_fn(custom_restore)
        result = get_bookmark_restore_dir_fn(MISSING)
        # Result should be the async-wrapped version
        assert result is not None
        assert callable(result)
