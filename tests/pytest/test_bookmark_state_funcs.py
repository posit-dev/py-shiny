"""Tests for shiny.bookmark._bookmark_state module"""

import os
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from shiny.bookmark._bookmark_state import (
    _local_dir,
    local_restore_dir,
    local_save_dir,
    shiny_bookmarks_folder_name,
)


class TestShinyBookmarksFolderName:
    """Test shiny_bookmarks_folder_name constant"""

    def test_folder_name_value(self):
        """Test shiny_bookmarks_folder_name has expected value"""
        assert shiny_bookmarks_folder_name == "shiny_bookmarks"

    def test_folder_name_is_string(self):
        """Test shiny_bookmarks_folder_name is a string"""
        assert isinstance(shiny_bookmarks_folder_name, str)


class TestLocalDir:
    """Test _local_dir function"""

    def test_local_dir_returns_path(self):
        """Test _local_dir returns a Path object"""
        result = _local_dir("test_id")
        assert isinstance(result, Path)

    def test_local_dir_includes_bookmarks_folder(self):
        """Test _local_dir includes shiny_bookmarks folder"""
        result = _local_dir("test_id")
        assert shiny_bookmarks_folder_name in str(result)

    def test_local_dir_includes_id(self):
        """Test _local_dir includes the bookmark id"""
        result = _local_dir("my_bookmark_123")
        assert "my_bookmark_123" in str(result)

    def test_local_dir_uses_cwd(self):
        """Test _local_dir is relative to current working directory"""
        result = _local_dir("test")
        cwd = Path(os.getcwd())
        # The path should start with the current working directory
        assert str(result).startswith(str(cwd))

    def test_local_dir_path_structure(self):
        """Test _local_dir has correct path structure"""
        result = _local_dir("bookmark_abc")
        # Should be cwd / shiny_bookmarks / id
        expected_end = Path(shiny_bookmarks_folder_name) / "bookmark_abc"
        assert str(result).endswith(str(expected_end))


class TestLocalSaveDir:
    """Test local_save_dir async function"""

    @pytest.mark.asyncio
    async def test_local_save_dir_creates_directory(
        self, tmp_path: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """Test local_save_dir creates directory if not exists"""
        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        result = await local_save_dir("new_bookmark")

        # Directory should be created
        assert result.exists()
        assert result.is_dir()

    @pytest.mark.asyncio
    async def test_local_save_dir_returns_path(
        self, tmp_path: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """Test local_save_dir returns Path object"""
        monkeypatch.chdir(tmp_path)

        result = await local_save_dir("test_id")

        assert isinstance(result, Path)

    @pytest.mark.asyncio
    async def test_local_save_dir_creates_nested(
        self, tmp_path: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """Test local_save_dir creates nested directories"""
        monkeypatch.chdir(tmp_path)

        result = await local_save_dir("nested_id")

        # Should create shiny_bookmarks/nested_id
        assert shiny_bookmarks_folder_name in str(result)
        assert "nested_id" in str(result)
        assert result.exists()


class TestLocalRestoreDir:
    """Test local_restore_dir async function"""

    @pytest.mark.asyncio
    async def test_local_restore_dir_returns_path(
        self, tmp_path: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """Test local_restore_dir returns Path object"""
        monkeypatch.chdir(tmp_path)

        result = await local_restore_dir("test_id")

        assert isinstance(result, Path)

    @pytest.mark.asyncio
    async def test_local_restore_dir_doesnt_create(
        self, tmp_path: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """Test local_restore_dir doesn't create directory"""
        monkeypatch.chdir(tmp_path)

        result = await local_restore_dir("nonexistent_id")

        # Should return path but not create it
        assert not result.exists()

    @pytest.mark.asyncio
    async def test_local_restore_dir_structure(
        self, tmp_path: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """Test local_restore_dir returns correct path structure"""
        monkeypatch.chdir(tmp_path)

        result = await local_restore_dir("restore_test")

        assert "shiny_bookmarks" in str(result)
        assert "restore_test" in str(result)
