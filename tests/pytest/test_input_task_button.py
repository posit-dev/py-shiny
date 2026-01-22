"""Tests for shiny.ui._input_task_button module."""

from shiny.ui import input_task_button


class TestInputTaskButton:
    """Tests for input_task_button function."""

    def test_input_task_button_basic(self):
        """Test basic input_task_button creation."""
        btn = input_task_button("task_btn", "Run Task")
        # The button is wrapped - let's just verify it's a valid Tag
        assert btn is not None
        html = str(btn)
        assert "task_btn" in html
        assert "Run Task" in html

    def test_input_task_button_with_icon(self):
        """Test input_task_button with icon."""
        btn = input_task_button("task_btn", "Run Task", icon="🚀")
        html = str(btn)
        assert "🚀" in html

    def test_input_task_button_with_busy_label(self):
        """Test input_task_button with custom busy label."""
        btn = input_task_button("task_btn", "Run Task", label_busy="Working...")
        html = str(btn)
        assert "Working..." in html

    def test_input_task_button_with_width(self):
        """Test input_task_button with width."""
        btn = input_task_button("task_btn", "Run Task", width="200px")
        html = str(btn)
        assert "200px" in html

    def test_input_task_button_type(self):
        """Test input_task_button with different types."""
        btn = input_task_button("task_btn", "Run Task", type="success")
        html = str(btn)
        assert "btn-success" in html

    def test_input_task_button_type_none(self):
        """Test input_task_button with no type."""
        btn = input_task_button("task_btn", "Run Task", type=None)
        # Should still render without error
        assert btn is not None

    def test_input_task_button_auto_reset(self):
        """Test input_task_button with auto_reset."""
        btn_auto = input_task_button("task_btn", "Run Task", auto_reset=True)
        btn_manual = input_task_button("task_btn2", "Run Task", auto_reset=False)
        html_auto = str(btn_auto)
        html_manual = str(btn_manual)
        # auto_reset should be reflected in the data attribute
        assert "data-auto-reset" in html_auto or "data-auto-reset" in html_manual

    def test_input_task_button_with_kwargs(self):
        """Test input_task_button with additional attributes."""
        btn = input_task_button(
            "task_btn", "Run Task", class_="custom-class", data_value="test"
        )
        html = str(btn)
        assert "custom-class" in html
        assert "data-value" in html
