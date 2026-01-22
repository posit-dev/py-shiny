"""Tests for shiny/ui/_insert.py - Insert/Remove UI functions."""

import pytest

from shiny.ui._insert import insert_ui, remove_ui


class TestInsertUiSignature:
    """Tests for insert_ui function signature."""

    def test_insert_ui_callable(self):
        """Test insert_ui is callable."""
        assert callable(insert_ui)

    def test_insert_ui_requires_session(self):
        """Test insert_ui raises when no session."""
        with pytest.raises(RuntimeError, match="session"):
            insert_ui(
                ui="<div>test</div>",
                selector="#container",
            )


class TestRemoveUiSignature:
    """Tests for remove_ui function signature."""

    def test_remove_ui_callable(self):
        """Test remove_ui is callable."""
        assert callable(remove_ui)

    def test_remove_ui_requires_session(self):
        """Test remove_ui raises when no session."""
        with pytest.raises(RuntimeError, match="session"):
            remove_ui(selector="#container")


class TestInsertUiAll:
    """Tests for __all__ exports."""

    def test_insert_ui_in_all(self):
        """Test insert_ui is in __all__."""
        from shiny.ui._insert import __all__

        assert "insert_ui" in __all__

    def test_remove_ui_in_all(self):
        """Test remove_ui is in __all__."""
        from shiny.ui._insert import __all__

        assert "remove_ui" in __all__
