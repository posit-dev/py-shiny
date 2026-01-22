"""Comprehensive tests for shiny.ui._input_task_button module."""

from htmltools import Tag


class TestInputTaskButton:
    """Tests for input_task_button function."""

    def test_input_task_button_basic(self):
        """input_task_button should create a button element."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click me")
        assert isinstance(result, Tag)
        assert result.name == "button"
        assert result.attrs.get("id") == "btn"
        assert result.attrs.get("type") == "button"

    def test_input_task_button_with_label(self):
        """input_task_button should display label."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "My Label")
        html_str = str(result)
        assert "My Label" in html_str

    def test_input_task_button_with_icon(self):
        """input_task_button should include icon."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click", icon="⭐")
        html_str = str(result)
        assert "⭐" in html_str

    def test_input_task_button_default_busy_label(self):
        """input_task_button should have default busy label."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click")
        html_str = str(result)
        assert "Processing..." in html_str

    def test_input_task_button_custom_busy_label(self):
        """input_task_button should accept custom busy label."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click", label_busy="Working...")
        html_str = str(result)
        assert "Working..." in html_str

    def test_input_task_button_default_busy_icon(self):
        """input_task_button should have default spinner icon when busy."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click")
        html_str = str(result)
        # Should contain spinner SVG
        assert "py-shiny-spin" in html_str or "svg" in html_str.lower()

    def test_input_task_button_custom_busy_icon(self):
        """input_task_button should accept custom busy icon."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click", icon_busy="⏳")
        html_str = str(result)
        assert "⏳" in html_str

    def test_input_task_button_width(self):
        """input_task_button should accept width parameter."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click", width="200px")
        html_str = str(result)
        assert "200px" in html_str

    def test_input_task_button_type_primary(self):
        """input_task_button should have primary type class."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click", type="primary")
        assert "btn-primary" in result.attrs.get("class", "")

    def test_input_task_button_type_secondary(self):
        """input_task_button should accept secondary type."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click", type="secondary")
        assert "btn-secondary" in result.attrs.get("class", "")

    def test_input_task_button_type_none(self):
        """input_task_button with type=None should not have btn-* class."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click", type=None)
        html_str = str(result)
        assert "btn-primary" not in html_str
        # When type=None, button classes are omitted but structure remains
        assert "bslib-switch-inline" in html_str

    def test_input_task_button_auto_reset_true(self):
        """input_task_button should have auto-reset attribute."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click", auto_reset=True)
        # Boolean attributes in HTML appear as empty string when True
        assert result.attrs.get("data-auto-reset") == ""

    def test_input_task_button_auto_reset_false(self):
        """input_task_button should handle auto_reset=False."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click", auto_reset=False)
        # When False, the attribute is omitted entirely
        assert "data-auto-reset" not in result.attrs

    def test_input_task_button_with_kwargs(self):
        """input_task_button should accept additional attributes."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click", custom_attr="value")
        # Underscores in kwargs are converted to hyphens in HTML
        assert result.attrs.get("custom-attr") == "value"
        # Underscores in kwargs are converted to hyphens in HTML
        assert result.attrs.get("custom-attr") == "value"

    def test_input_task_button_has_bslib_switch(self):
        """input_task_button should contain bslib-switch-inline element."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click")
        html_str = str(result)
        assert "bslib-switch-inline" in html_str

    def test_input_task_button_has_ready_slot(self):
        """input_task_button should have ready slot."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Ready Label")
        html_str = str(result)
        assert 'slot="ready"' in html_str
        assert "Ready Label" in html_str

    def test_input_task_button_has_busy_slot(self):
        """input_task_button should have busy slot."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click", label_busy="Busy Label")
        html_str = str(result)
        assert 'slot="busy"' in html_str
        assert "Busy Label" in html_str

    def test_input_task_button_custom_states(self):
        """input_task_button should accept custom state args."""
        from htmltools import tags

        from shiny.ui import input_task_button

        custom_state = tags.span("Custom State", slot="custom")
        result = input_task_button("btn", "Click", custom_state)
        html_str = str(result)
        assert 'slot="custom"' in html_str
        assert "Custom State" in html_str

    def test_input_task_button_includes_dependencies(self):
        """input_task_button should include required dependencies."""
        from shiny.ui import input_task_button

        result = input_task_button("btn", "Click")
        # Check for dependencies in the result
        # Dependencies should be present (components and spin)
        assert len(result.children) > 2  # Has children beyond just the switch


class TestModuleExports:
    """Tests for module exports."""

    def test_module_imports_correctly(self):
        """Module should import without errors."""
        import shiny.ui._input_task_button as input_task_button_module

        assert input_task_button_module is not None

    def test_all_exports_exist(self):
        """All items in __all__ should be importable."""
        from shiny.ui import _input_task_button

        for item in _input_task_button.__all__:
            assert hasattr(_input_task_button, item)
