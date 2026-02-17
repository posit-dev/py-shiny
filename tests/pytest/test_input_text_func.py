"""Tests for shiny.ui._input_text module."""

from shiny.ui import input_text, input_text_area


class TestInputText:
    """Tests for the input_text function."""

    def test_basic_text(self):
        """Test creating a basic text input."""
        result = input_text("text1", "Enter text:")
        html = str(result)

        assert 'id="text1"' in html
        assert "Enter text:" in html
        assert 'type="text"' in html
        assert "shiny-input-text" in html
        assert "form-control" in html

    def test_text_with_value(self):
        """Test text input with initial value."""
        result = input_text("text2", "Name:", value="John")
        html = str(result)

        assert 'value="John"' in html

    def test_text_with_placeholder(self):
        """Test text input with placeholder."""
        result = input_text("text3", "Email:", placeholder="you@example.com")
        html = str(result)

        assert 'placeholder="you@example.com"' in html

    def test_text_with_width(self):
        """Test text input with custom width."""
        result = input_text("text4", "Text:", width="300px")
        html = str(result)

        assert "300px" in html

    def test_text_with_autocomplete(self):
        """Test text input with autocomplete setting."""
        result = input_text("text5", "Username:", autocomplete="username")
        html = str(result)

        assert 'autocomplete="username"' in html

    def test_text_with_autocomplete_on(self):
        """Test text input with autocomplete on."""
        result = input_text("text6", "Name:", autocomplete="on")
        html = str(result)

        assert 'autocomplete="on"' in html

    def test_text_with_autocomplete_none(self):
        """Test text input with autocomplete None."""
        result = input_text("text7", "Text:", autocomplete=None)
        html = str(result)

        # autocomplete should not be in the output
        assert "autocomplete=" not in html

    def test_text_with_spellcheck_true(self):
        """Test text input with spellcheck enabled."""
        result = input_text("text8", "Content:", spellcheck="true")
        html = str(result)

        assert 'spellcheck="true"' in html

    def test_text_with_spellcheck_false(self):
        """Test text input with spellcheck disabled."""
        result = input_text("text9", "Code:", spellcheck="false")
        html = str(result)

        assert 'spellcheck="false"' in html

    def test_text_with_update_on_change(self):
        """Test text input with update_on=change."""
        result = input_text("text10", "Text:", update_on="change")
        html = str(result)

        assert 'data-update-on="change"' in html

    def test_text_with_update_on_blur(self):
        """Test text input with update_on=blur."""
        result = input_text("text11", "Text:", update_on="blur")
        html = str(result)

        assert 'data-update-on="blur"' in html


class TestInputTextArea:
    """Tests for the input_text_area function."""

    def test_basic_textarea(self):
        """Test creating a basic text area."""
        result = input_text_area("area1", "Comments:")
        html = str(result)

        assert 'id="area1"' in html
        assert "Comments:" in html
        assert "<textarea" in html
        assert "shiny-input-textarea" in html

    def test_textarea_with_value(self):
        """Test text area with initial value."""
        result = input_text_area("area2", "Notes:", value="Initial text")
        html = str(result)

        assert "Initial text" in html

    def test_textarea_with_width(self):
        """Test text area with custom width."""
        result = input_text_area("area3", "Text:", width="400px")
        html = str(result)

        assert "400px" in html

    def test_textarea_with_height(self):
        """Test text area with custom height."""
        result = input_text_area("area4", "Text:", height="200px")
        html = str(result)

        assert "200px" in html

    def test_textarea_with_rows(self):
        """Test text area with rows attribute."""
        result = input_text_area("area5", "Text:", rows=10)
        html = str(result)

        assert 'rows="10"' in html

    def test_textarea_with_cols(self):
        """Test text area with cols attribute."""
        result = input_text_area("area6", "Text:", cols=40)
        html = str(result)

        assert 'cols="40"' in html

    def test_textarea_with_placeholder(self):
        """Test text area with placeholder."""
        result = input_text_area("area7", "Bio:", placeholder="Tell us about yourself")
        html = str(result)

        assert 'placeholder="Tell us about yourself"' in html

    def test_textarea_with_autocomplete(self):
        """Test text area with autocomplete setting."""
        result = input_text_area("area8", "Address:", autocomplete="street-address")
        html = str(result)

        assert 'autocomplete="street-address"' in html

    def test_textarea_with_spellcheck(self):
        """Test text area with spellcheck setting."""
        result = input_text_area("area9", "Content:", spellcheck="true")
        html = str(result)

        assert 'spellcheck="true"' in html

    def test_textarea_with_resize(self):
        """Test text area with resize setting."""
        result = input_text_area("area10", "Text:", resize="vertical")
        html = str(result)

        assert "resize" in html or "vertical" in html

    def test_textarea_with_autoresize(self):
        """Test text area with autoresize enabled."""
        result = input_text_area("area11", "Text:", autoresize=True)
        html = str(result)

        assert 'id="area11"' in html

    def test_textarea_with_update_on(self):
        """Test text area with update_on setting."""
        result = input_text_area("area12", "Text:", update_on="blur")
        html = str(result)

        assert 'data-update-on="blur"' in html
