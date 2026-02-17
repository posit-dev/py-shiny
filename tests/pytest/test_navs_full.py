"""Tests for shiny/ui/_navs.py module."""

from shiny.ui._navs import (
    nav_menu,
    nav_panel,
    navset_bar,
    navset_card_pill,
    navset_card_tab,
    navset_pill,
    navset_tab,
)


class TestNavPanel:
    """Tests for nav_panel function."""

    def test_nav_panel_is_callable(self):
        """Test nav_panel is callable."""
        assert callable(nav_panel)

    def test_nav_panel_returns_nav_set(self):
        """Test nav_panel returns appropriate object."""
        from shiny.ui._navs import NavPanel

        result = nav_panel("Tab 1", "Content 1")
        assert isinstance(result, NavPanel)


class TestNavMenu:
    """Tests for nav_menu function."""

    def test_nav_menu_is_callable(self):
        """Test nav_menu is callable."""
        assert callable(nav_menu)

    def test_nav_menu_returns_nav_menu(self):
        """Test nav_menu returns NavMenu object."""
        from shiny.ui._navs import NavMenu

        result = nav_menu("Menu", nav_panel("Item 1", "Content 1"))
        assert isinstance(result, NavMenu)


class TestNavsetBar:
    """Tests for navset_bar function."""

    def test_navset_bar_is_callable(self):
        """Test navset_bar is callable."""
        assert callable(navset_bar)


class TestNavsetCardTab:
    """Tests for navset_card_tab function."""

    def test_navset_card_tab_is_callable(self):
        """Test navset_card_tab is callable."""
        assert callable(navset_card_tab)


class TestNavsetCardPill:
    """Tests for navset_card_pill function."""

    def test_navset_card_pill_is_callable(self):
        """Test navset_card_pill is callable."""
        assert callable(navset_card_pill)


class TestNavsetTab:
    """Tests for navset_tab function."""

    def test_navset_tab_is_callable(self):
        """Test navset_tab is callable."""
        assert callable(navset_tab)

    def test_navset_tab_returns_navset(self):
        """Test navset_tab returns a NavSet object."""
        from shiny.ui._navs import NavSet

        result = navset_tab(nav_panel("Tab 1", "Content 1"))
        assert isinstance(result, NavSet)


class TestNavsetPill:
    """Tests for navset_pill function."""

    def test_navset_pill_is_callable(self):
        """Test navset_pill is callable."""
        assert callable(navset_pill)


class TestNavsExported:
    """Tests for navs functions export."""

    def test_nav_panel_in_ui(self):
        """Test nav_panel is in ui module."""
        from shiny import ui

        assert hasattr(ui, "nav_panel")

    def test_navset_tab_in_ui(self):
        """Test navset_tab is in ui module."""
        from shiny import ui

        assert hasattr(ui, "navset_tab")

    def test_navset_pill_in_ui(self):
        """Test navset_pill is in ui module."""
        from shiny import ui

        assert hasattr(ui, "navset_pill")

    def test_navset_card_tab_in_ui(self):
        """Test navset_card_tab is in ui module."""
        from shiny import ui

        assert hasattr(ui, "navset_card_tab")

    def test_navset_bar_in_ui(self):
        """Test navset_bar is in ui module."""
        from shiny import ui

        assert hasattr(ui, "navset_bar")
