"""Tests for various input UI components."""

from shiny.ui import (
    input_action_button,
    input_action_link,
    input_checkbox,
    input_checkbox_group,
    input_date,
    input_date_range,
    input_numeric,
    input_password,
    input_radio_buttons,
    input_slider,
    input_switch,
    input_text,
    input_text_area,
)


class TestInputNumeric:
    """Tests for the input_numeric function."""

    def test_basic_numeric(self):
        """Test creating a basic numeric input."""
        inp = input_numeric("my_num", "Number:", 10)
        html = str(inp)

        assert 'id="my_num"' in html
        assert "Number:" in html
        assert 'value="10"' in html
        assert 'type="number"' in html

    def test_numeric_with_min_max(self):
        """Test numeric input with min and max values."""
        inp = input_numeric("my_num", "Number:", 50, min=0, max=100)
        html = str(inp)

        assert 'min="0"' in html
        assert 'max="100"' in html

    def test_numeric_with_step(self):
        """Test numeric input with step value."""
        inp = input_numeric("my_num", "Number:", 0, step=0.1)
        html = str(inp)

        assert 'step="0.1"' in html

    def test_numeric_with_width(self):
        """Test numeric input with custom width."""
        inp = input_numeric("my_num", "Number:", 0, width="200px")
        html = str(inp)

        assert "200px" in html


class TestInputText:
    """Tests for the input_text function."""

    def test_basic_text(self):
        """Test creating a basic text input."""
        inp = input_text("my_text", "Enter text:")
        html = str(inp)

        assert 'id="my_text"' in html
        assert "Enter text:" in html
        assert 'type="text"' in html

    def test_text_with_value(self):
        """Test text input with initial value."""
        inp = input_text("my_text", "Name:", value="John")
        html = str(inp)

        assert 'value="John"' in html

    def test_text_with_placeholder(self):
        """Test text input with placeholder."""
        inp = input_text("my_text", "Email:", placeholder="you@example.com")
        html = str(inp)

        assert 'placeholder="you@example.com"' in html

    def test_text_with_width(self):
        """Test text input with custom width."""
        inp = input_text("my_text", "Text:", width="300px")
        html = str(inp)

        assert "300px" in html


class TestInputPassword:
    """Tests for the input_password function."""

    def test_basic_password(self):
        """Test creating a basic password input."""
        inp = input_password("my_pass", "Password:")
        html = str(inp)

        assert 'id="my_pass"' in html
        assert "Password:" in html
        assert 'type="password"' in html

    def test_password_with_value(self):
        """Test password input with initial value."""
        inp = input_password("my_pass", "Password:", value="secret")
        html = str(inp)

        assert 'value="secret"' in html


class TestInputTextArea:
    """Tests for the input_text_area function."""

    def test_basic_text_area(self):
        """Test creating a basic text area."""
        inp = input_text_area("my_area", "Comments:")
        html = str(inp)

        assert 'id="my_area"' in html
        assert "Comments:" in html
        assert "<textarea" in html

    def test_text_area_with_value(self):
        """Test text area with initial value."""
        inp = input_text_area("my_area", "Notes:", value="Initial text")
        html = str(inp)

        assert "Initial text" in html

    def test_text_area_with_dimensions(self):
        """Test text area with explicit dimensions."""
        inp = input_text_area("my_area", "Text:", rows=10, cols=40)
        html = str(inp)

        assert 'rows="10"' in html

    def test_text_area_with_placeholder(self):
        """Test text area with placeholder."""
        inp = input_text_area("my_area", "Bio:", placeholder="Tell us about yourself")
        html = str(inp)

        assert 'placeholder="Tell us about yourself"' in html


class TestInputSlider:
    """Tests for the input_slider function."""

    def test_basic_slider(self):
        """Test creating a basic slider input."""
        inp = input_slider("my_slider", "Value:", min=0, max=100, value=50)
        html = str(inp)

        assert 'id="my_slider"' in html
        assert "Value:" in html

    def test_slider_with_step(self):
        """Test slider with step value."""
        inp = input_slider("my_slider", "Value:", min=0, max=10, value=5, step=0.5)
        html = str(inp)

        assert 'id="my_slider"' in html

    def test_slider_range(self):
        """Test slider with range (two values)."""
        inp = input_slider("my_slider", "Range:", min=0, max=100, value=[25, 75])
        html = str(inp)

        assert 'id="my_slider"' in html


class TestInputCheckbox:
    """Tests for the input_checkbox function."""

    def test_basic_checkbox(self):
        """Test creating a basic checkbox."""
        inp = input_checkbox("my_check", "Accept terms")
        html = str(inp)

        assert 'id="my_check"' in html
        assert "Accept terms" in html
        assert 'type="checkbox"' in html

    def test_checkbox_checked(self):
        """Test checkbox that is initially checked."""
        inp = input_checkbox("my_check", "Enabled", value=True)
        html = str(inp)

        assert "checked" in html


class TestInputSwitch:
    """Tests for the input_switch function."""

    def test_basic_switch(self):
        """Test creating a basic switch input."""
        inp = input_switch("my_switch", "Enable feature")
        html = str(inp)

        assert 'id="my_switch"' in html
        assert "Enable feature" in html

    def test_switch_on(self):
        """Test switch that is initially on."""
        inp = input_switch("my_switch", "Active", value=True)
        html = str(inp)

        assert "checked" in html


class TestInputCheckboxGroup:
    """Tests for the input_checkbox_group function."""

    def test_basic_checkbox_group(self):
        """Test creating a basic checkbox group."""
        inp = input_checkbox_group(
            "my_group", "Select options:", choices=["A", "B", "C"]
        )
        html = str(inp)

        assert 'id="my_group"' in html
        assert "Select options:" in html
        assert "A" in html
        assert "B" in html
        assert "C" in html

    def test_checkbox_group_with_selected(self):
        """Test checkbox group with pre-selected values."""
        inp = input_checkbox_group(
            "my_group",
            "Options:",
            choices=["X", "Y", "Z"],
            selected=["X", "Z"],
        )
        html = str(inp)

        assert 'id="my_group"' in html

    def test_checkbox_group_inline(self):
        """Test checkbox group with inline layout."""
        inp = input_checkbox_group(
            "my_group", "Options:", choices=["A", "B"], inline=True
        )
        html = str(inp)

        assert "inline" in html


class TestInputRadioButtons:
    """Tests for the input_radio_buttons function."""

    def test_basic_radio_buttons(self):
        """Test creating basic radio buttons."""
        inp = input_radio_buttons(
            "my_radio", "Choose one:", choices=["Option 1", "Option 2", "Option 3"]
        )
        html = str(inp)

        assert 'id="my_radio"' in html
        assert "Choose one:" in html
        assert "Option 1" in html
        assert "Option 2" in html
        assert "Option 3" in html

    def test_radio_buttons_with_selected(self):
        """Test radio buttons with pre-selected value."""
        inp = input_radio_buttons(
            "my_radio",
            "Choice:",
            choices=["A", "B", "C"],
            selected="B",
        )
        html = str(inp)

        assert 'id="my_radio"' in html

    def test_radio_buttons_inline(self):
        """Test radio buttons with inline layout."""
        inp = input_radio_buttons("my_radio", "Pick:", choices=["X", "Y"], inline=True)
        html = str(inp)

        assert "inline" in html


class TestInputDate:
    """Tests for the input_date function."""

    def test_basic_date(self):
        """Test creating a basic date input."""
        inp = input_date("my_date", "Select date:")
        html = str(inp)

        assert 'id="my_date"' in html
        assert "Select date:" in html

    def test_date_with_value(self):
        """Test date input with initial value."""
        inp = input_date("my_date", "Date:", value="2024-01-15")
        html = str(inp)

        assert 'id="my_date"' in html

    def test_date_with_min_max(self):
        """Test date input with min and max dates."""
        inp = input_date("my_date", "Date:", min="2024-01-01", max="2024-12-31")
        html = str(inp)

        assert 'id="my_date"' in html


class TestInputDateRange:
    """Tests for the input_date_range function."""

    def test_basic_date_range(self):
        """Test creating a basic date range input."""
        inp = input_date_range("my_range", "Date range:")
        html = str(inp)

        assert 'id="my_range"' in html
        assert "Date range:" in html

    def test_date_range_with_values(self):
        """Test date range with initial start and end dates."""
        inp = input_date_range(
            "my_range", "Period:", start="2024-01-01", end="2024-12-31"
        )
        html = str(inp)

        assert 'id="my_range"' in html


class TestInputActionButton:
    """Tests for the input_action_button function."""

    def test_basic_action_button(self):
        """Test creating a basic action button."""
        btn = input_action_button("my_btn", "Click Me")
        html = str(btn)

        assert 'id="my_btn"' in html
        assert "Click Me" in html
        assert "<button" in html

    def test_action_button_with_icon(self):
        """Test action button with an icon."""
        from htmltools import tags

        icon = tags.i(class_="fa fa-play")
        btn = input_action_button("my_btn", "Start", icon=icon)
        html = str(btn)

        assert "fa-play" in html

    def test_action_button_with_class(self):
        """Test action button with custom class."""
        btn = input_action_button("my_btn", "Submit", class_="btn-primary")
        html = str(btn)

        assert "btn-primary" in html

    def test_action_button_disabled(self):
        """Test action button that is initially disabled."""
        btn = input_action_button("my_btn", "Disabled", disabled=True)
        html = str(btn)

        assert "disabled" in html


class TestInputActionLink:
    """Tests for the input_action_link function."""

    def test_basic_action_link(self):
        """Test creating a basic action link."""
        link = input_action_link("my_link", "Click here")
        html = str(link)

        assert 'id="my_link"' in html
        assert "Click here" in html
        assert "<a" in html

    def test_action_link_with_icon(self):
        """Test action link with an icon."""
        from htmltools import tags

        icon = tags.i(class_="fa fa-info")
        link = input_action_link("my_link", "Info", icon=icon)
        html = str(link)

        assert "fa-info" in html
