"""Unit tests for shiny.ui._navs module."""

from __future__ import annotations

from htmltools import tags

from shiny.ui import (
    nav_control,
    nav_menu,
    nav_panel,
    nav_spacer,
    navset_card_pill,
    navset_card_tab,
    navset_card_underline,
    navset_hidden,
    navset_pill,
    navset_pill_list,
    navset_tab,
    navset_underline,
)


class TestNavPanel:
    """Tests for nav_panel function."""

    def test_basic_nav_panel(self) -> None:
        """Test basic nav_panel creation."""
        panel = nav_panel("Tab 1", "Tab 1 content")
        assert panel.nav is not None
        assert panel.content is not None

    def test_nav_panel_with_value(self) -> None:
        """Test nav_panel with custom value."""
        panel = nav_panel("Tab 1", "Content", value="tab1")
        assert panel.get_value() == "tab1"

    def test_nav_panel_default_value_from_title(self) -> None:
        """Test nav_panel uses title as default value."""
        panel = nav_panel("My Tab Title", "Content")
        assert panel.get_value() == "My Tab Title"

    def test_nav_panel_with_icon(self) -> None:
        """Test nav_panel with icon."""
        icon = tags.i(class_="fa fa-home")
        panel = nav_panel("Home", "Content", icon=icon)
        html = str(panel.nav)
        assert "fa-home" in html

    def test_nav_panel_multiple_content(self) -> None:
        """Test nav_panel with multiple content children."""
        panel = nav_panel(
            "Tab",
            tags.p("First"),
            tags.p("Second"),
        )
        html = str(panel.content)
        assert "First" in html
        assert "Second" in html


class TestNavControl:
    """Tests for nav_control function."""

    def test_basic_nav_control(self) -> None:
        """Test basic nav_control creation."""
        control = nav_control(tags.span("Custom control"))
        assert control.nav is not None
        assert control.content is None

    def test_nav_control_with_button(self) -> None:
        """Test nav_control with button."""
        control = nav_control(tags.button("Click me", type="button"))
        html = str(control.nav)
        assert "Click me" in html

    def test_nav_control_get_value_none(self) -> None:
        """Test nav_control returns None for value."""
        control = nav_control(tags.span("Control"))
        assert control.get_value() is None


class TestNavSpacer:
    """Tests for nav_spacer function."""

    def test_basic_nav_spacer(self) -> None:
        """Test basic nav_spacer creation."""
        spacer = nav_spacer()
        assert spacer.nav is not None
        assert spacer.content is None

    def test_nav_spacer_has_class(self) -> None:
        """Test nav_spacer has appropriate class."""
        spacer = nav_spacer()
        html = str(spacer.nav)
        assert "bslib-nav-spacer" in html

    def test_nav_spacer_get_value_none(self) -> None:
        """Test nav_spacer returns None for value."""
        spacer = nav_spacer()
        assert spacer.get_value() is None


class TestNavMenu:
    """Tests for nav_menu function."""

    def test_basic_nav_menu(self) -> None:
        """Test basic nav_menu creation."""
        panel = nav_panel("Panel 1", "Content 1")
        menu = nav_menu("Menu", panel)
        assert menu.title is not None
        assert len(menu.nav_controls) > 0

    def test_nav_menu_with_value(self) -> None:
        """Test nav_menu with custom value."""
        panel = nav_panel("Panel 1", "Content 1")
        menu = nav_menu("Menu", panel, value="my_menu")
        assert menu.value == "my_menu"

    def test_nav_menu_default_value(self) -> None:
        """Test nav_menu uses title as default value."""
        panel = nav_panel("Panel 1", "Content 1")
        menu = nav_menu("My Menu", panel)
        assert menu.value == "My Menu"

    def test_nav_menu_align_left(self) -> None:
        """Test nav_menu with left alignment."""
        panel = nav_panel("Panel 1", "Content 1")
        menu = nav_menu("Menu", panel, align="left")
        assert menu.align == "left"

    def test_nav_menu_align_right(self) -> None:
        """Test nav_menu with right alignment."""
        panel = nav_panel("Panel 1", "Content 1")
        menu = nav_menu("Menu", panel, align="right")
        assert menu.align == "right"

    def test_nav_menu_with_icon(self) -> None:
        """Test nav_menu with icon."""
        panel = nav_panel("Panel 1", "Content 1")
        icon = tags.i(class_="fa fa-cog")
        menu = nav_menu("Menu", panel, icon=icon)
        # Icon should be part of title
        assert menu.title is not None


class TestNavsetTab:
    """Tests for navset_tab function."""

    def test_basic_navset_tab(self) -> None:
        """Test basic navset_tab creation."""
        result = navset_tab(
            nav_panel("Tab 1", "Content 1"),
            nav_panel("Tab 2", "Content 2"),
        )
        # navset_tab returns a NavSet which is tagifiable
        html = str(result.tagify())
        assert "Tab 1" in html
        assert "Tab 2" in html

    def test_navset_tab_with_id(self) -> None:
        """Test navset_tab with id."""
        result = navset_tab(
            nav_panel("Tab 1", "Content 1"),
            id="my_tabs",
        )
        html = str(result.tagify())
        assert "my_tabs" in html

    def test_navset_tab_with_selected(self) -> None:
        """Test navset_tab with selected tab."""
        result = navset_tab(
            nav_panel("Tab 1", "Content 1", value="t1"),
            nav_panel("Tab 2", "Content 2", value="t2"),
            selected="t2",
        )
        html = str(result.tagify())
        assert "Tab 1" in html
        assert "Tab 2" in html


class TestNavsetPill:
    """Tests for navset_pill function."""

    def test_basic_navset_pill(self) -> None:
        """Test basic navset_pill creation."""
        result = navset_pill(
            nav_panel("Pill 1", "Content 1"),
            nav_panel("Pill 2", "Content 2"),
        )
        html = str(result.tagify())
        assert "Pill 1" in html
        assert "Pill 2" in html

    def test_navset_pill_with_id(self) -> None:
        """Test navset_pill with id."""
        result = navset_pill(
            nav_panel("Pill 1", "Content 1"),
            id="my_pills",
        )
        html = str(result.tagify())
        assert "my_pills" in html


class TestNavsetUnderline:
    """Tests for navset_underline function."""

    def test_basic_navset_underline(self) -> None:
        """Test basic navset_underline creation."""
        result = navset_underline(
            nav_panel("Tab 1", "Content 1"),
            nav_panel("Tab 2", "Content 2"),
        )
        html = str(result.tagify())
        assert "Tab 1" in html

    def test_navset_underline_with_id(self) -> None:
        """Test navset_underline with id."""
        result = navset_underline(
            nav_panel("Tab 1", "Content 1"),
            id="my_underline",
        )
        html = str(result.tagify())
        assert "my_underline" in html


class TestNavsetCardTab:
    """Tests for navset_card_tab function."""

    def test_basic_navset_card_tab(self) -> None:
        """Test basic navset_card_tab creation."""
        result = navset_card_tab(
            nav_panel("Tab 1", "Content 1"),
            nav_panel("Tab 2", "Content 2"),
        )
        html = str(result.tagify())
        assert "Tab 1" in html
        assert "card" in html

    def test_navset_card_tab_with_id(self) -> None:
        """Test navset_card_tab with id."""
        result = navset_card_tab(
            nav_panel("Tab 1", "Content 1"),
            id="my_card_tabs",
        )
        html = str(result.tagify())
        assert "my_card_tabs" in html

    def test_navset_card_tab_with_title(self) -> None:
        """Test navset_card_tab with title."""
        result = navset_card_tab(
            nav_panel("Tab 1", "Content 1"),
            title="Card Title",
        )
        html = str(result.tagify())
        assert "Card Title" in html


class TestNavsetCardPill:
    """Tests for navset_card_pill function."""

    def test_basic_navset_card_pill(self) -> None:
        """Test basic navset_card_pill creation."""
        result = navset_card_pill(
            nav_panel("Pill 1", "Content 1"),
            nav_panel("Pill 2", "Content 2"),
        )
        html = str(result.tagify())
        assert "Pill 1" in html
        assert "card" in html

    def test_navset_card_pill_with_id(self) -> None:
        """Test navset_card_pill with id."""
        result = navset_card_pill(
            nav_panel("Pill 1", "Content 1"),
            id="my_card_pills",
        )
        html = str(result.tagify())
        assert "my_card_pills" in html


class TestNavsetCardUnderline:
    """Tests for navset_card_underline function."""

    def test_basic_navset_card_underline(self) -> None:
        """Test basic navset_card_underline creation."""
        result = navset_card_underline(
            nav_panel("Tab 1", "Content 1"),
            nav_panel("Tab 2", "Content 2"),
        )
        html = str(result.tagify())
        assert "Tab 1" in html
        assert "card" in html


class TestNavsetPillList:
    """Tests for navset_pill_list function."""

    def test_basic_navset_pill_list(self) -> None:
        """Test basic navset_pill_list creation."""
        result = navset_pill_list(
            nav_panel("Pill 1", "Content 1"),
            nav_panel("Pill 2", "Content 2"),
        )
        html = str(result.tagify())
        assert "Pill 1" in html

    def test_navset_pill_list_with_id(self) -> None:
        """Test navset_pill_list with id."""
        result = navset_pill_list(
            nav_panel("Pill 1", "Content 1"),
            id="my_pill_list",
        )
        html = str(result.tagify())
        assert "my_pill_list" in html

    def test_navset_pill_list_widths(self) -> None:
        """Test navset_pill_list with custom widths."""
        result = navset_pill_list(
            nav_panel("Pill 1", "Content 1"),
            widths=(3, 9),
        )
        html = str(result.tagify())
        assert "Pill 1" in html


class TestNavsetHidden:
    """Tests for navset_hidden function."""

    def test_basic_navset_hidden(self) -> None:
        """Test basic navset_hidden creation."""
        result = navset_hidden(
            nav_panel("Tab 1", "Content 1"),
            nav_panel("Tab 2", "Content 2"),
        )
        html = str(result.tagify())
        assert "Content 1" in html
        assert "Content 2" in html

    def test_navset_hidden_with_id(self) -> None:
        """Test navset_hidden with id."""
        result = navset_hidden(
            nav_panel("Tab 1", "Content 1"),
            id="my_hidden",
        )
        html = str(result.tagify())
        assert "my_hidden" in html

    def test_navset_hidden_with_selected(self) -> None:
        """Test navset_hidden with selected panel."""
        result = navset_hidden(
            nav_panel("Tab 1", "Content 1", value="t1"),
            nav_panel("Tab 2", "Content 2", value="t2"),
            selected="t2",
        )
        html = str(result.tagify())
        # The hidden navset should render but hide the nav items
        assert "Content 1" in html
