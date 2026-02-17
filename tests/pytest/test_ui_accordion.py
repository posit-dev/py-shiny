"""Tests for shiny/ui/_accordion.py"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from htmltools import Tag

from shiny.ui._accordion import (
    AccordionPanel,
    accordion,
    accordion_panel,
    insert_accordion_panel,
    remove_accordion_panel,
    update_accordion,
    update_accordion_panel,
)


def create_mock_session() -> MagicMock:
    """Create a mock session for testing accordion functions."""
    mock = MagicMock()
    mock._process_ui.return_value = {"html": "<div>test</div>", "deps": []}
    return mock


class TestAccordionPanel:
    """Tests for accordion_panel function."""

    def test_accordion_panel_basic(self) -> None:
        """Test basic accordion panel creation."""
        panel = accordion_panel("Title", "Content")
        assert isinstance(panel, AccordionPanel)
        assert panel._data_value == "Title"
        assert panel._title == "Title"

    def test_accordion_panel_with_value(self) -> None:
        """Test accordion panel with custom value."""
        panel = accordion_panel("Title", "Content", value="custom-value")
        assert panel._data_value == "custom-value"

    def test_accordion_panel_with_icon(self) -> None:
        """Test accordion panel with icon."""
        panel = accordion_panel("Title", "Content", icon="★")
        assert panel._icon == "★"

    def test_accordion_panel_non_string_title_no_value_raises(self) -> None:
        """Test that non-string title without value raises error."""
        from htmltools import div

        with pytest.raises(ValueError):
            accordion_panel(div("Title"), "Content")

    def test_accordion_panel_value_must_be_string(self) -> None:
        """Test that value must be a string."""
        with pytest.raises(TypeError):
            accordion_panel("Title", "Content", value=123)  # type: ignore


class TestAccordion:
    """Tests for accordion function."""

    def test_accordion_basic(self) -> None:
        """Test basic accordion creation."""
        result = accordion(accordion_panel("Tab1", "Content1"))
        assert isinstance(result, Tag)
        html = str(result)
        assert "accordion" in html

    def test_accordion_multiple_panels(self) -> None:
        """Test accordion with multiple panels."""
        result = accordion(
            accordion_panel("Tab1", "Content1"),
            accordion_panel("Tab2", "Content2"),
            accordion_panel("Tab3", "Content3"),
        )
        html = str(result)
        assert "Tab1" in html
        assert "Tab2" in html
        assert "Tab3" in html

    def test_accordion_with_id(self) -> None:
        """Test accordion with id."""
        result = accordion(accordion_panel("Tab1", "Content"), id="my_accordion")
        html = str(result)
        assert "my_accordion" in html

    def test_accordion_open_first_by_default(self) -> None:
        """Test that first panel is open by default."""
        result = accordion(
            accordion_panel("Tab1", "Content1"),
            accordion_panel("Tab2", "Content2"),
        )
        html = str(result)
        assert 'aria-expanded="true"' in html

    def test_accordion_open_none(self) -> None:
        """Test accordion with no panels open."""
        result = accordion(
            accordion_panel("Tab1", "Content1"),
            accordion_panel("Tab2", "Content2"),
            open=False,
        )
        html = str(result)
        assert html.count('aria-expanded="false"') == 2

    def test_accordion_open_all(self) -> None:
        """Test accordion with all panels open."""
        result = accordion(
            accordion_panel("Tab1", "Content1"),
            accordion_panel("Tab2", "Content2"),
            open=True,
        )
        html = str(result)
        assert html.count('aria-expanded="true"') == 2

    def test_accordion_open_specific(self) -> None:
        """Test accordion with specific panel open."""
        result = accordion(
            accordion_panel("Tab1", "Content1", value="tab1"),
            accordion_panel("Tab2", "Content2", value="tab2"),
            open="tab2",
        )
        html = str(result)
        assert "show" in html

    def test_accordion_multiple_false_only_one_open(self) -> None:
        """Test that multiple=False allows only one panel open."""
        result = accordion(
            accordion_panel("Tab1", "Content1"),
            accordion_panel("Tab2", "Content2"),
            multiple=False,
        )
        html = str(result)
        assert "autoclose" in html

    def test_accordion_multiple_false_error_on_multiple_open(self) -> None:
        """Test error when multiple=False but multiple open specified."""
        with pytest.raises(ValueError):
            accordion(
                accordion_panel("Tab1", "C1", value="t1"),
                accordion_panel("Tab2", "C2", value="t2"),
                multiple=False,
                open=["t1", "t2"],
            )

    def test_accordion_with_width_height(self) -> None:
        """Test accordion with custom width and height."""
        result = accordion(
            accordion_panel("Tab1", "Content"), width="400px", height="300px"
        )
        html = str(result)
        assert "400px" in html
        assert "300px" in html

    def test_accordion_non_panel_raises(self) -> None:
        """Test that non-AccordionPanel items raise error."""
        with pytest.raises(TypeError):
            accordion("not a panel")  # type: ignore


class TestUpdateAccordion:
    """Tests for update_accordion function."""

    def test_update_accordion_show_panel(self) -> None:
        """Test showing specific panel."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._accordion.require_active_session", return_value=mock_session
        ):
            update_accordion("acc", show="panel1", session=mock_session)
        mock_session.on_flush.assert_called_once()

    def test_update_accordion_show_all(self) -> None:
        """Test showing all panels."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._accordion.require_active_session", return_value=mock_session
        ):
            update_accordion("acc", show=True, session=mock_session)
        mock_session.on_flush.assert_called_once()

    def test_update_accordion_hide_all(self) -> None:
        """Test hiding all panels."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._accordion.require_active_session", return_value=mock_session
        ):
            update_accordion("acc", show=False, session=mock_session)
        mock_session.on_flush.assert_called_once()


class TestInsertAccordionPanel:
    """Tests for insert_accordion_panel function."""

    def test_insert_accordion_panel_after(self) -> None:
        """Test inserting panel after target."""
        mock_session = create_mock_session()
        panel = accordion_panel("New", "Content")
        with patch(
            "shiny.ui._accordion.require_active_session", return_value=mock_session
        ):
            insert_accordion_panel(
                "acc", panel, target="existing", position="after", session=mock_session
            )
        mock_session.on_flush.assert_called_once()

    def test_insert_accordion_panel_before(self) -> None:
        """Test inserting panel before target."""
        mock_session = create_mock_session()
        panel = accordion_panel("New", "Content")
        with patch(
            "shiny.ui._accordion.require_active_session", return_value=mock_session
        ):
            insert_accordion_panel(
                "acc", panel, target="existing", position="before", session=mock_session
            )
        mock_session.on_flush.assert_called_once()

    def test_insert_accordion_panel_invalid_position(self) -> None:
        """Test that invalid position raises error."""
        mock_session = create_mock_session()
        panel = accordion_panel("New", "Content")
        with patch(
            "shiny.ui._accordion.require_active_session", return_value=mock_session
        ):
            with pytest.raises(ValueError):
                insert_accordion_panel(
                    "acc", panel, position="invalid", session=mock_session  # type: ignore
                )


class TestRemoveAccordionPanel:
    """Tests for remove_accordion_panel function."""

    def test_remove_accordion_panel_single(self) -> None:
        """Test removing single panel."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._accordion.require_active_session", return_value=mock_session
        ):
            remove_accordion_panel("acc", "panel1", session=mock_session)
        mock_session.on_flush.assert_called_once()

    def test_remove_accordion_panel_multiple(self) -> None:
        """Test removing multiple panels."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._accordion.require_active_session", return_value=mock_session
        ):
            remove_accordion_panel("acc", ["panel1", "panel2"], session=mock_session)
        mock_session.on_flush.assert_called_once()


class TestUpdateAccordionPanel:
    """Tests for update_accordion_panel function."""

    def test_update_accordion_panel_title(self) -> None:
        """Test updating panel title."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._accordion.require_active_session", return_value=mock_session
        ):
            update_accordion_panel(
                "acc", "panel1", title="New Title", session=mock_session
            )
        mock_session.on_flush.assert_called()

    def test_update_accordion_panel_body(self) -> None:
        """Test updating panel body."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._accordion.require_active_session", return_value=mock_session
        ):
            update_accordion_panel(
                "acc", "panel1", "New body content", session=mock_session
            )
        mock_session.on_flush.assert_called()

    def test_update_accordion_panel_show(self) -> None:
        """Test showing a panel."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._accordion.require_active_session", return_value=mock_session
        ):
            update_accordion_panel("acc", "panel1", show=True, session=mock_session)
        mock_session.on_flush.assert_called()

    def test_update_accordion_panel_hide(self) -> None:
        """Test hiding a panel."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._accordion.require_active_session", return_value=mock_session
        ):
            update_accordion_panel("acc", "panel1", show=False, session=mock_session)
        mock_session.on_flush.assert_called()

    def test_update_accordion_panel_value(self) -> None:
        """Test updating panel value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._accordion.require_active_session", return_value=mock_session
        ):
            update_accordion_panel(
                "acc", "panel1", value="new-value", session=mock_session
            )
        mock_session.on_flush.assert_called()
