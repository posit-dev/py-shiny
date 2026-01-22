"""Tests for shiny/ui/_navs_dynamic.py - Dynamic nav functions."""

import pytest

from shiny.ui._navs_dynamic import insert_nav_panel, remove_nav_panel, update_nav_panel


class TestInsertNavPanelSignature:
    """Tests for insert_nav_panel function signature."""

    def test_insert_nav_panel_callable(self):
        """Test insert_nav_panel is callable."""
        assert callable(insert_nav_panel)

    def test_insert_nav_panel_requires_session(self):
        """Test insert_nav_panel raises when no session."""
        from shiny import ui

        with pytest.raises(RuntimeError, match="session"):
            insert_nav_panel(
                id="navset",
                nav_panel=ui.nav_panel("Tab", "content"),
            )


class TestRemoveNavPanelSignature:
    """Tests for remove_nav_panel function signature."""

    def test_remove_nav_panel_callable(self):
        """Test remove_nav_panel is callable."""
        assert callable(remove_nav_panel)

    def test_remove_nav_panel_requires_session(self):
        """Test remove_nav_panel raises when no session."""
        with pytest.raises(RuntimeError, match="session"):
            remove_nav_panel(id="navset", target="tab1")


class TestUpdateNavPanelSignature:
    """Tests for update_nav_panel function signature."""

    def test_update_nav_panel_callable(self):
        """Test update_nav_panel is callable."""
        assert callable(update_nav_panel)

    def test_update_nav_panel_requires_session(self):
        """Test update_nav_panel raises when no session."""
        with pytest.raises(RuntimeError, match="session"):
            update_nav_panel(
                id="navset",
                target="tab1",
                method="show",
            )


class TestNavsDynamicAll:
    """Tests for __all__ exports."""

    def test_insert_nav_panel_in_all(self):
        """Test insert_nav_panel is in __all__."""
        from shiny.ui._navs_dynamic import __all__

        assert "insert_nav_panel" in __all__

    def test_remove_nav_panel_in_all(self):
        """Test remove_nav_panel is in __all__."""
        from shiny.ui._navs_dynamic import __all__

        assert "remove_nav_panel" in __all__

    def test_update_nav_panel_in_all(self):
        """Test update_nav_panel is in __all__."""
        from shiny.ui._navs_dynamic import __all__

        assert "update_nav_panel" in __all__
