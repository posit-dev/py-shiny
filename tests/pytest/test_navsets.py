"""Tests for navigation set UI components."""

from shiny.ui import (
    nav_panel,
    nav_menu,
    nav_control,
    nav_spacer,
    navset_tab,
    navset_pill,
    navset_underline,
    navset_hidden,
    navset_card_tab,
    navset_card_pill,
    navset_card_underline,
    navset_pill_list,
    navset_bar,
)


class TestNavPanel:
    """Tests for the nav_panel function."""

    def test_basic_nav_panel(self):
        """Test creating a basic nav panel."""
        panel = nav_panel("Tab Title", "Tab content")
        assert panel is not None
        assert panel.get_value() == "Tab Title"

    def test_nav_panel_with_value(self):
        """Test nav panel with explicit value."""
        panel = nav_panel("Display Title", "Content", value="tab_id")
        assert panel.get_value() == "tab_id"

    def test_nav_panel_with_icon(self):
        """Test nav panel with icon."""
        from htmltools import tags

        icon = tags.i(class_="fa fa-home")
        panel = nav_panel("Home", "Home content", icon=icon)
        assert panel is not None


class TestNavMenu:
    """Tests for the nav_menu function."""

    def test_basic_nav_menu(self):
        """Test creating a basic nav menu."""
        menu = nav_menu(
            "Menu",
            nav_panel("Option 1", "Content 1"),
            nav_panel("Option 2", "Content 2"),
        )
        assert menu is not None


class TestNavControl:
    """Tests for the nav_control function."""

    def test_basic_nav_control(self):
        """Test creating a nav control."""
        from shiny.ui import input_text

        control = nav_control(input_text("search", "", placeholder="Search..."))
        assert control is not None


class TestNavSpacer:
    """Tests for the nav_spacer function."""

    def test_basic_nav_spacer(self):
        """Test creating a nav spacer."""
        spacer = nav_spacer()
        assert spacer is not None


class TestNavsetTab:
    """Tests for the navset_tab function."""

    def test_basic_navset_tab(self):
        """Test creating a basic tab navset."""
        navset = navset_tab(
            nav_panel("Tab 1", "Content 1"),
            nav_panel("Tab 2", "Content 2"),
        )
        assert navset is not None

    def test_navset_tab_with_id(self):
        """Test tab navset with id."""
        navset = navset_tab(nav_panel("Tab 1", "Content 1"), id="my_tabs")
        assert navset is not None

    def test_navset_tab_with_selected(self):
        """Test tab navset with selected tab."""
        navset = navset_tab(
            nav_panel("Tab 1", "Content 1"),
            nav_panel("Tab 2", "Content 2"),
            selected="Tab 2",
        )
        assert navset is not None


class TestNavsetPill:
    """Tests for the navset_pill function."""

    def test_basic_navset_pill(self):
        """Test creating a basic pill navset."""
        navset = navset_pill(
            nav_panel("Pill 1", "Content 1"),
            nav_panel("Pill 2", "Content 2"),
        )
        assert navset is not None


class TestNavsetUnderline:
    """Tests for the navset_underline function."""

    def test_basic_navset_underline(self):
        """Test creating a basic underline navset."""
        navset = navset_underline(
            nav_panel("Item 1", "Content 1"),
            nav_panel("Item 2", "Content 2"),
        )
        assert navset is not None


class TestNavsetHidden:
    """Tests for the navset_hidden function."""

    def test_basic_navset_hidden(self):
        """Test creating a hidden navset."""
        navset = navset_hidden(
            nav_panel("Panel 1", "Content 1"),
            nav_panel("Panel 2", "Content 2"),
            id="hidden_navs",
        )
        assert navset is not None


class TestNavsetCardTab:
    """Tests for the navset_card_tab function."""

    def test_basic_navset_card_tab(self):
        """Test creating a basic card tab navset."""
        navset = navset_card_tab(
            nav_panel("Tab 1", "Content 1"),
            nav_panel("Tab 2", "Content 2"),
        )
        assert navset is not None


class TestNavsetCardPill:
    """Tests for the navset_card_pill function."""

    def test_basic_navset_card_pill(self):
        """Test creating a basic card pill navset."""
        navset = navset_card_pill(
            nav_panel("Pill 1", "Content 1"),
            nav_panel("Pill 2", "Content 2"),
        )
        assert navset is not None


class TestNavsetCardUnderline:
    """Tests for the navset_card_underline function."""

    def test_basic_navset_card_underline(self):
        """Test creating a basic card underline navset."""
        navset = navset_card_underline(
            nav_panel("Item 1", "Content 1"),
            nav_panel("Item 2", "Content 2"),
        )
        assert navset is not None


class TestNavsetPillList:
    """Tests for the navset_pill_list function."""

    def test_basic_navset_pill_list(self):
        """Test creating a basic pill list navset."""
        navset = navset_pill_list(
            nav_panel("Item 1", "Content 1"),
            nav_panel("Item 2", "Content 2"),
        )
        assert navset is not None


class TestNavsetBar:
    """Tests for the navset_bar function."""

    def test_basic_navset_bar(self):
        """Test creating a basic navbar navset."""
        navset = navset_bar(
            nav_panel("Tab 1", "Content 1"),
            nav_panel("Tab 2", "Content 2"),
            title="My Navbar",
        )
        assert navset is not None
