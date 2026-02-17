"""Tests for shiny.ui._navs module - NavPanel and nav functions."""

import pytest
from htmltools import tags

from shiny.ui._navs import (
    NavMenu,
    NavPanel,
    nav_control,
    nav_menu,
    nav_panel,
    nav_spacer,
)


class TestNavPanel:
    """Tests for NavPanel class."""

    def test_nav_panel_init(self) -> None:
        """Test NavPanel initialization."""
        nav = tags.li("test")
        panel = NavPanel(nav)
        assert panel.nav is nav
        assert panel.content is None

    def test_nav_panel_with_content(self) -> None:
        """Test NavPanel with content."""
        nav = tags.li("test")
        content = tags.div("content")
        panel = NavPanel(nav, content)
        assert panel.nav is nav
        assert panel.content is content

    def test_nav_panel_get_value_none_content(self) -> None:
        """Test get_value returns None when content is None."""
        panel = NavPanel(tags.li("test"))
        assert panel.get_value() is None

    def test_nav_panel_resolve_none_content(self) -> None:
        """Test resolve returns nav and None when content is None."""
        nav = tags.li("spacer")
        panel = NavPanel(nav)
        resolved_nav, resolved_content = panel.resolve(None, {})
        assert resolved_nav is nav
        assert resolved_content is None

    def test_nav_panel_tagify_raises(self) -> None:
        """Test that tagify raises NotImplementedError."""
        panel = NavPanel(tags.li("test"))
        with pytest.raises(NotImplementedError):
            panel.tagify()


class TestNavPanelFunction:
    """Tests for nav_panel function."""

    def test_nav_panel_basic(self) -> None:
        """Test basic nav_panel creation."""
        result = nav_panel("Tab 1", "Content 1")
        assert isinstance(result, NavPanel)
        assert result.nav is not None
        assert result.content is not None

    def test_nav_panel_with_value(self) -> None:
        """Test nav_panel with explicit value."""
        result = nav_panel("Tab 1", "Content 1", value="tab1")
        assert result.get_value() == "tab1"

    def test_nav_panel_value_defaults_to_title(self) -> None:
        """Test nav_panel value defaults to title."""
        result = nav_panel("My Tab", "Content")
        assert result.get_value() == "My Tab"

    def test_nav_panel_with_icon(self) -> None:
        """Test nav_panel with icon."""
        icon = tags.i(class_="bi-house")
        result = nav_panel("Home", "Content", icon=icon)
        assert isinstance(result, NavPanel)

    def test_nav_panel_multiple_content(self) -> None:
        """Test nav_panel with multiple content elements."""
        result = nav_panel("Tab", "Content 1", "Content 2", tags.p("Paragraph"))
        assert isinstance(result, NavPanel)
        assert result.content is not None


class TestNavControl:
    """Tests for nav_control function."""

    def test_nav_control_basic(self) -> None:
        """Test basic nav_control creation."""
        result = nav_control("Custom control")
        assert isinstance(result, NavPanel)
        assert result.content is None

    def test_nav_control_with_tag(self) -> None:
        """Test nav_control with Tag."""
        result = nav_control(tags.button("Click me"))
        assert isinstance(result, NavPanel)

    def test_nav_control_multiple_elements(self) -> None:
        """Test nav_control with multiple elements."""
        result = nav_control("Text", tags.span("Span"), tags.a("Link"))
        assert isinstance(result, NavPanel)

    def test_nav_control_get_value_none(self) -> None:
        """Test nav_control returns None for get_value."""
        result = nav_control("Control")
        assert result.get_value() is None


class TestNavSpacer:
    """Tests for nav_spacer function."""

    def test_nav_spacer_basic(self) -> None:
        """Test basic nav_spacer creation."""
        result = nav_spacer()
        assert isinstance(result, NavPanel)
        assert result.content is None

    def test_nav_spacer_has_class(self) -> None:
        """Test nav_spacer has bslib-nav-spacer class."""
        result = nav_spacer()
        html = str(result.nav)
        assert "bslib-nav-spacer" in html

    def test_nav_spacer_get_value_none(self) -> None:
        """Test nav_spacer returns None for get_value."""
        result = nav_spacer()
        assert result.get_value() is None


class TestNavMenu:
    """Tests for NavMenu class."""

    def test_nav_menu_init(self) -> None:
        """Test NavMenu initialization."""
        panel1 = nav_panel("Tab 1", "Content 1")
        menu = NavMenu(panel1, title="Menu", value="menu1")
        assert menu.title == "Menu"
        assert menu.value == "menu1"
        assert menu.align == "left"

    def test_nav_menu_with_align(self) -> None:
        """Test NavMenu with align parameter."""
        panel1 = nav_panel("Tab 1", "Content 1")
        menu = NavMenu(panel1, title="Menu", value="menu1", align="right")
        assert menu.align == "right"

    def test_nav_menu_with_multiple_items(self) -> None:
        """Test NavMenu with multiple nav items."""
        panel1 = nav_panel("Tab 1", "Content 1")
        panel2 = nav_panel("Tab 2", "Content 2")
        menu = NavMenu(panel1, panel2, title="Dropdown", value="dropdown")
        assert len(menu.nav_controls) == 2


class TestNavMenuFunction:
    """Tests for nav_menu function."""

    def test_nav_menu_basic(self) -> None:
        """Test basic nav_menu creation."""
        panel = nav_panel("Tab", "Content")
        result = nav_menu("Menu", panel)
        assert isinstance(result, NavMenu)

    def test_nav_menu_with_value(self) -> None:
        """Test nav_menu with explicit value."""
        panel = nav_panel("Tab", "Content")
        result = nav_menu("Menu", panel, value="custom_value")
        assert result.value == "custom_value"

    def test_nav_menu_with_icon(self) -> None:
        """Test nav_menu with icon."""
        panel = nav_panel("Tab", "Content")
        icon = tags.i(class_="bi-menu")
        result = nav_menu("Menu", panel, icon=icon)
        assert isinstance(result, NavMenu)

    def test_nav_menu_with_align_right(self) -> None:
        """Test nav_menu with right alignment."""
        panel = nav_panel("Tab", "Content")
        result = nav_menu("Menu", panel, align="right")
        assert result.align == "right"

    def test_nav_menu_default_value_from_title(self) -> None:
        """Test nav_menu default value comes from title."""
        panel = nav_panel("Tab", "Content")
        result = nav_menu("My Menu", panel)
        assert result.value == "My Menu"
