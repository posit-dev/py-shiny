"""Unit tests for shiny.ui._input_text module."""

from __future__ import annotations

import pytest

from shiny.ui import input_text, input_text_area


class TestInputText:
    """Tests for input_text function."""

    def test_basic_input_text(self) -> None:
        """Test basic input_text with required parameters."""
        result = input_text("my_id", "My Label")
        html = str(result)

        assert 'id="my_id"' in html
        assert "My Label" in html
        assert "form-group" in html
        assert "shiny-input-container" in html
        assert 'type="text"' in html

    def test_input_text_with_value(self) -> None:
        """Test input_text with initial value."""
        result = input_text("my_id", "Label", value="initial value")
        html = str(result)

        assert 'value="initial value"' in html

    def test_input_text_with_width(self) -> None:
        """Test input_text with width parameter."""
        result = input_text("my_id", "Label", width="400px")
        html = str(result)

        assert "width:400px" in html

    def test_input_text_with_placeholder(self) -> None:
        """Test input_text with placeholder text."""
        result = input_text("my_id", "Label", placeholder="Enter text here")
        html = str(result)

        assert 'placeholder="Enter text here"' in html

    def test_input_text_with_autocomplete_on(self) -> None:
        """Test input_text with autocomplete enabled."""
        result = input_text("my_id", "Label", autocomplete="on")
        html = str(result)

        assert 'autocomplete="on"' in html

    def test_input_text_with_autocomplete_off(self) -> None:
        """Test input_text with autocomplete disabled."""
        result = input_text("my_id", "Label", autocomplete="off")
        html = str(result)

        assert 'autocomplete="off"' in html

    def test_input_text_with_autocomplete_email(self) -> None:
        """Test input_text with autocomplete set to email."""
        result = input_text("my_id", "Label", autocomplete="email")
        html = str(result)

        assert 'autocomplete="email"' in html

    def test_input_text_with_spellcheck_true(self) -> None:
        """Test input_text with spellcheck enabled."""
        result = input_text("my_id", "Label", spellcheck="true")
        html = str(result)

        assert 'spellcheck="true"' in html

    def test_input_text_with_spellcheck_false(self) -> None:
        """Test input_text with spellcheck disabled."""
        result = input_text("my_id", "Label", spellcheck="false")
        html = str(result)

        assert 'spellcheck="false"' in html

    def test_input_text_update_on_change(self) -> None:
        """Test input_text with update_on='change'."""
        result = input_text("my_id", "Label", update_on="change")
        html = str(result)

        assert 'data-update-on="change"' in html

    def test_input_text_update_on_blur(self) -> None:
        """Test input_text with update_on='blur'."""
        result = input_text("my_id", "Label", update_on="blur")
        html = str(result)

        assert 'data-update-on="blur"' in html

    def test_input_text_returns_tag(self) -> None:
        """Test that input_text returns a Tag."""
        from htmltools import Tag

        result = input_text("my_id", "Label")
        assert isinstance(result, Tag)

    def test_input_text_with_all_parameters(self) -> None:
        """Test input_text with all parameters set."""
        result = input_text(
            "full_id",
            "Full Label",
            value="preset",
            width="300px",
            placeholder="Type here",
            autocomplete="username",
            spellcheck="false",
            update_on="blur",
        )
        html = str(result)

        assert 'id="full_id"' in html
        assert "Full Label" in html
        assert 'value="preset"' in html
        assert "width:300px" in html
        assert 'placeholder="Type here"' in html
        assert 'autocomplete="username"' in html
        assert 'spellcheck="false"' in html
        assert 'data-update-on="blur"' in html

    def test_input_text_empty_label(self) -> None:
        """Test input_text with empty label."""
        result = input_text("my_id", "")
        html = str(result)

        assert 'id="my_id"' in html

    def test_input_text_html_label(self) -> None:
        """Test input_text with HTML label."""
        from htmltools import tags

        label = tags.strong("Bold Label")
        result = input_text("my_id", label)
        html = str(result)

        assert "<strong>Bold Label</strong>" in html

    def test_input_text_default_update_on(self) -> None:
        """Test input_text default update_on is 'change'."""
        result = input_text("my_id", "Label")
        html = str(result)

        assert 'data-update-on="change"' in html

    def test_input_text_form_control_class(self) -> None:
        """Test that input element has form-control class."""
        result = input_text("my_id", "Label")
        html = str(result)

        assert "form-control" in html
        assert "shiny-input-text" in html


class TestInputTextArea:
    """Tests for input_text_area function."""

    def test_basic_input_text_area(self) -> None:
        """Test basic input_text_area with required parameters."""
        result = input_text_area("ta_id", "TextArea Label")
        html = str(result)

        assert 'id="ta_id"' in html
        assert "TextArea Label" in html
        assert 'class="shiny-input-textarea form-group shiny-input-container"' in html
        assert "<textarea" in html

    def test_input_text_area_with_value(self) -> None:
        """Test input_text_area with initial value."""
        result = input_text_area("ta_id", "Label", value="initial content")
        html = str(result)

        assert "initial content" in html

    def test_input_text_area_with_width(self) -> None:
        """Test input_text_area with width parameter."""
        result = input_text_area("ta_id", "Label", width="500px")
        html = str(result)

        assert "width:500px" in html

    def test_input_text_area_with_height(self) -> None:
        """Test input_text_area with height parameter."""
        result = input_text_area("ta_id", "Label", height="200px")
        html = str(result)

        assert "height:200px" in html

    def test_input_text_area_with_cols(self) -> None:
        """Test input_text_area with cols parameter."""
        result = input_text_area("ta_id", "Label", cols=80)
        html = str(result)

        assert 'cols="80"' in html

    def test_input_text_area_with_rows(self) -> None:
        """Test input_text_area with rows parameter."""
        result = input_text_area("ta_id", "Label", rows=10)
        html = str(result)

        assert 'rows="10"' in html

    def test_input_text_area_with_placeholder(self) -> None:
        """Test input_text_area with placeholder."""
        result = input_text_area("ta_id", "Label", placeholder="Enter description")
        html = str(result)

        assert 'placeholder="Enter description"' in html

    def test_input_text_area_resize_none(self) -> None:
        """Test input_text_area with resize='none'."""
        result = input_text_area("ta_id", "Label", resize="none")
        html = str(result)

        assert "resize:none" in html

    def test_input_text_area_resize_both(self) -> None:
        """Test input_text_area with resize='both'."""
        result = input_text_area("ta_id", "Label", resize="both")
        html = str(result)

        assert "resize:both" in html

    def test_input_text_area_resize_horizontal(self) -> None:
        """Test input_text_area with resize='horizontal'."""
        result = input_text_area("ta_id", "Label", resize="horizontal")
        html = str(result)

        assert "resize:horizontal" in html

    def test_input_text_area_resize_vertical(self) -> None:
        """Test input_text_area with resize='vertical'."""
        result = input_text_area("ta_id", "Label", resize="vertical")
        html = str(result)

        assert "resize:vertical" in html

    def test_input_text_area_invalid_resize(self) -> None:
        """Test input_text_area with invalid resize value raises error."""
        with pytest.raises(ValueError, match="Invalid resize value"):
            input_text_area("ta_id", "Label", resize="invalid")  # type: ignore

    def test_input_text_area_autoresize(self) -> None:
        """Test input_text_area with autoresize enabled."""
        result = input_text_area("ta_id", "Label", autoresize=True)
        html = str(result)

        assert "textarea-autoresize" in html

    def test_input_text_area_autoresize_default_rows(self) -> None:
        """Test input_text_area autoresize sets default rows to 1."""
        result = input_text_area("ta_id", "Label", autoresize=True)
        html = str(result)

        assert 'rows="1"' in html

    def test_input_text_area_autoresize_custom_rows(self) -> None:
        """Test input_text_area autoresize with custom rows."""
        result = input_text_area("ta_id", "Label", autoresize=True, rows=5)
        html = str(result)

        assert 'rows="5"' in html

    def test_input_text_area_autocomplete(self) -> None:
        """Test input_text_area with autocomplete."""
        result = input_text_area("ta_id", "Label", autocomplete="on")
        html = str(result)

        assert 'autocomplete="on"' in html

    def test_input_text_area_spellcheck_true(self) -> None:
        """Test input_text_area with spellcheck true."""
        result = input_text_area("ta_id", "Label", spellcheck="true")
        html = str(result)

        assert 'spellcheck="true"' in html

    def test_input_text_area_spellcheck_false(self) -> None:
        """Test input_text_area with spellcheck false."""
        result = input_text_area("ta_id", "Label", spellcheck="false")
        html = str(result)

        assert 'spellcheck="false"' in html

    def test_input_text_area_update_on_change(self) -> None:
        """Test input_text_area with update_on='change'."""
        result = input_text_area("ta_id", "Label", update_on="change")
        html = str(result)

        assert 'data-update-on="change"' in html

    def test_input_text_area_update_on_blur(self) -> None:
        """Test input_text_area with update_on='blur'."""
        result = input_text_area("ta_id", "Label", update_on="blur")
        html = str(result)

        assert 'data-update-on="blur"' in html

    def test_input_text_area_returns_tag(self) -> None:
        """Test that input_text_area returns a Tag."""
        from htmltools import Tag

        result = input_text_area("ta_id", "Label")
        assert isinstance(result, Tag)

    def test_input_text_area_with_all_parameters(self) -> None:
        """Test input_text_area with all parameters."""
        result = input_text_area(
            "full_ta_id",
            "Full TextArea",
            value="preset content",
            width="600px",
            height="400px",
            cols=100,
            rows=20,
            placeholder="Enter text",
            resize="both",
            autoresize=False,
            autocomplete="off",
            spellcheck="false",
            update_on="blur",
        )
        html = str(result)

        assert 'id="full_ta_id"' in html
        assert "Full TextArea" in html
        assert "preset content" in html
        assert "width:600px" in html
        assert "height:400px" in html
        assert 'cols="100"' in html
        assert 'rows="20"' in html
        assert 'placeholder="Enter text"' in html
        assert "resize:both" in html
        assert 'autocomplete="off"' in html
        assert 'spellcheck="false"' in html
        assert 'data-update-on="blur"' in html

    def test_input_text_area_form_control_class(self) -> None:
        """Test that textarea element has form-control class."""
        result = input_text_area("ta_id", "Label")
        html = str(result)

        assert "form-control" in html

    def test_input_text_area_default_width_style(self) -> None:
        """Test input_text_area default width style when width not specified."""
        result = input_text_area("ta_id", "Label")
        html = str(result)

        # When width is not specified, textarea should have width:100% style
        assert "width:100%" in html

    def test_input_text_area_html_label(self) -> None:
        """Test input_text_area with HTML label."""
        from htmltools import tags

        label = tags.em("Italic Label")
        result = input_text_area("ta_id", label)
        html = str(result)

        assert "<em>Italic Label</em>" in html

    def test_input_text_area_multiline_value(self) -> None:
        """Test input_text_area with multiline value."""
        result = input_text_area("ta_id", "Label", value="Line 1\nLine 2\nLine 3")
        html = str(result)

        assert "Line 1" in html
        assert "Line 2" in html
        assert "Line 3" in html
