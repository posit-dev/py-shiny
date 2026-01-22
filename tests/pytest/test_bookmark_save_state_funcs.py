"""Tests for shiny.bookmark._save_state module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shiny.bookmark._save_state import BookmarkState


class TestBookmarkState:
    """Tests for BookmarkState class."""

    def test_bookmark_state_init(self):
        """BookmarkState should initialize with given parameters."""
        mock_input = MagicMock()
        exclude = ["input1", "input2"]
        state = BookmarkState(
            input=mock_input,
            exclude=exclude,
            on_save=None,
        )

        assert state.input is mock_input
        assert state.exclude == exclude
        assert state._on_save is None
        assert state.dir is None
        assert state.values == {}

    def test_bookmark_state_init_with_on_save(self):
        """BookmarkState should initialize with on_save callback."""
        mock_input = MagicMock()
        mock_on_save = AsyncMock()

        state = BookmarkState(
            input=mock_input,
            exclude=[],
            on_save=mock_on_save,
        )

        assert state._on_save is mock_on_save

    def test_bookmark_state_values_is_dict(self):
        """BookmarkState.values should be an empty dict initially."""
        mock_input = MagicMock()
        state = BookmarkState(
            input=mock_input,
            exclude=[],
            on_save=None,
        )

        assert isinstance(state.values, dict)
        assert len(state.values) == 0

    def test_bookmark_state_dir_is_none_initially(self):
        """BookmarkState.dir should be None initially."""
        mock_input = MagicMock()
        state = BookmarkState(
            input=mock_input,
            exclude=[],
            on_save=None,
        )

        assert state.dir is None

    def test_bookmark_state_can_modify_values(self):
        """BookmarkState.values can be modified."""
        mock_input = MagicMock()
        state = BookmarkState(
            input=mock_input,
            exclude=[],
            on_save=None,
        )

        state.values["custom_key"] = "custom_value"
        assert state.values["custom_key"] == "custom_value"

    def test_bookmark_state_exclude_is_list(self):
        """BookmarkState.exclude should be a list."""
        mock_input = MagicMock()
        state = BookmarkState(
            input=mock_input,
            exclude=["a", "b", "c"],
            on_save=None,
        )

        assert isinstance(state.exclude, list)
        assert len(state.exclude) == 3


@pytest.mark.asyncio
class TestBookmarkStateCallOnSave:
    """Tests for BookmarkState._call_on_save method."""

    async def test_call_on_save_with_no_callback(self):
        """_call_on_save should do nothing if no callback set."""
        mock_input = MagicMock()
        state = BookmarkState(
            input=mock_input,
            exclude=[],
            on_save=None,
        )

        # Should not raise
        await state._call_on_save()

    async def test_call_on_save_calls_callback(self):
        """_call_on_save should call the on_save callback."""
        mock_input = MagicMock()
        mock_on_save = AsyncMock()

        state = BookmarkState(
            input=mock_input,
            exclude=[],
            on_save=mock_on_save,
        )

        with patch("shiny.bookmark._save_state.isolate"):
            await state._call_on_save()

        mock_on_save.assert_called_once_with(state)
