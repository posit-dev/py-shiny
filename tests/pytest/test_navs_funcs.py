"""Tests for shiny.ui._navs module."""

from shiny.ui._navs import (
    NavSetBar,
    NavSetCard,
    nav_panel,
    navset_bar,
    navset_card_pill,
    navset_card_tab,
    navset_hidden,
)


class TestNavsetCardTab:
    """Tests for navset_card_tab function."""

    def test_navset_card_tab_basic(self) -> None:
        """Test basic navset_card_tab creation."""
        result = navset_card_tab(
            nav_panel("Tab 1", "Content 1"),
        )
        assert isinstance(result, NavSetCard)

    def test_navset_card_tab_multiple_panels(self) -> None:
        """Test navset_card_tab with multiple panels."""
        result = navset_card_tab(
            nav_panel("Tab 1", "Content 1"),
            nav_panel("Tab 2", "Content 2"),
        )
        html = str(result.tagify())
        assert "Tab 1" in html
        assert "Tab 2" in html

    def test_navset_card_tab_with_id(self) -> None:
        """Test navset_card_tab with id parameter."""
        result = navset_card_tab(
            nav_panel("Tab 1", "Content 1"),
            id="my_tabs",
        )
        html = str(result.tagify())
        assert "my_tabs" in html

    def test_navset_card_tab_with_title(self) -> None:
        """Test navset_card_tab with title parameter."""
        result = navset_card_tab(
            nav_panel("Tab 1", "Content 1"),
            title="Card Title",
        )
        html = str(result.tagify())
        assert "Card Title" in html


class TestNavsetCardPill:
    """Tests for navset_card_pill function."""

    def test_navset_card_pill_basic(self) -> None:
        """Test basic navset_card_pill creation."""
        result = navset_card_pill(
            nav_panel("Pill 1", "Content 1"),
        )
        assert isinstance(result, NavSetCard)

    def test_navset_card_pill_multiple_panels(self) -> None:
        """Test navset_card_pill with multiple panels."""
        result = navset_card_pill(
            nav_panel("Pill 1", "Content 1"),
            nav_panel("Pill 2", "Content 2"),
        )
        html = str(result.tagify())
        assert "Pill 1" in html
        assert "Pill 2" in html

    def test_navset_card_pill_with_id(self) -> None:
        """Test navset_card_pill with id parameter."""
        result = navset_card_pill(
            nav_panel("Pill 1", "Content 1"),
            id="my_pills",
        )
        html = str(result.tagify())
        assert "my_pills" in html


class TestNavsetBar:
    """Tests for navset_bar function."""

    def test_navset_bar_basic(self) -> None:
        """Test basic navset_bar creation."""
        result = navset_bar(
            nav_panel("Page 1", "Content 1"),
            title="My App",
        )
        assert isinstance(result, NavSetBar)

    def test_navset_bar_with_title(self) -> None:
        """Test navset_bar with title."""
        result = navset_bar(
            nav_panel("Page 1", "Content 1"),
            title="App Title",
        )
        html = str(result.tagify())
        assert "App Title" in html

    def test_navset_bar_multiple_panels(self) -> None:
        """Test navset_bar with multiple panels."""
        result = navset_bar(
            nav_panel("Page 1", "Content 1"),
            nav_panel("Page 2", "Content 2"),
            title="App",
        )
        html = str(result.tagify())
        assert "Page 1" in html
        assert "Page 2" in html

    def test_navset_bar_with_id(self) -> None:
        """Test navset_bar with id parameter."""
        result = navset_bar(
            nav_panel("Page 1", "Content 1"),
            title="App",
            id="my_navbar",
        )
        html = str(result.tagify())
        assert "my_navbar" in html


class TestNavsetHidden:
    """Tests for navset_hidden function."""

    def test_navset_hidden_basic(self) -> None:
        """Test basic navset_hidden creation."""
        result = navset_hidden(
            nav_panel("Panel 1", "Content 1", value="p1"),
        )
        # navset_hidden returns a NavSet object
        assert result is not None

    def test_navset_hidden_multiple_panels(self) -> None:
        """Test navset_hidden with multiple panels."""
        result = navset_hidden(
            nav_panel("Panel 1", "Content 1", value="p1"),
            nav_panel("Panel 2", "Content 2", value="p2"),
        )
        html = str(result.tagify())
        assert "Content 1" in html or "Content 2" in html

    def test_navset_hidden_with_id(self) -> None:
        """Test navset_hidden with id parameter."""
        result = navset_hidden(
            nav_panel("Panel 1", "Content 1", value="p1"),
            id="hidden_nav",
        )
        html = str(result.tagify())
        assert "hidden_nav" in html
