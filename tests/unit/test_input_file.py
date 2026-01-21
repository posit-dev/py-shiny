"""Unit tests for shiny.ui._input_file module."""

from __future__ import annotations

from htmltools import Tag

from shiny.ui import input_file


class TestInputFile:
    """Tests for input_file function."""

    def test_basic_input_file(self) -> None:
        """Test basic input_file with required parameters."""
        result = input_file("file_id", "Upload File")
        html = str(result)

        assert 'id="file_id"' in html
        assert "Upload File" in html
        assert 'type="file"' in html

    def test_input_file_returns_tag(self) -> None:
        """Test that input_file returns a Tag."""
        result = input_file("file_id", "Upload")
        assert isinstance(result, Tag)

    def test_input_file_multiple_true(self) -> None:
        """Test input_file with multiple=True."""
        result = input_file("file_id", "Upload", multiple=True)
        html = str(result)

        assert 'multiple="multiple"' in html

    def test_input_file_multiple_false(self) -> None:
        """Test input_file with multiple=False (default)."""
        result = input_file("file_id", "Upload", multiple=False)
        html = str(result)

        # multiple attribute should not be present
        assert "multiple=" not in html or 'multiple="multiple"' not in html

    def test_input_file_accept_string(self) -> None:
        """Test input_file with accept as string."""
        result = input_file("file_id", "Upload", accept=".csv")
        html = str(result)

        assert 'accept=".csv"' in html

    def test_input_file_accept_list(self) -> None:
        """Test input_file with accept as list."""
        result = input_file("file_id", "Upload", accept=[".csv", ".xlsx"])
        html = str(result)

        assert 'accept=".csv,.xlsx"' in html

    def test_input_file_accept_mime_type(self) -> None:
        """Test input_file with MIME type accept."""
        result = input_file("file_id", "Upload", accept="text/plain")
        html = str(result)

        assert 'accept="text/plain"' in html

    def test_input_file_accept_image_wildcard(self) -> None:
        """Test input_file with image/* accept."""
        result = input_file("file_id", "Upload", accept="image/*")
        html = str(result)

        assert 'accept="image/*"' in html

    def test_input_file_accept_video_wildcard(self) -> None:
        """Test input_file with video/* accept."""
        result = input_file("file_id", "Upload", accept="video/*")
        html = str(result)

        assert 'accept="video/*"' in html

    def test_input_file_accept_audio_wildcard(self) -> None:
        """Test input_file with audio/* accept."""
        result = input_file("file_id", "Upload", accept="audio/*")
        html = str(result)

        assert 'accept="audio/*"' in html

    def test_input_file_with_width(self) -> None:
        """Test input_file with width parameter."""
        result = input_file("file_id", "Upload", width="400px")
        html = str(result)

        assert "width:400px" in html

    def test_input_file_button_label(self) -> None:
        """Test input_file with custom button label."""
        result = input_file("file_id", "Upload", button_label="Choose File")
        html = str(result)

        assert "Choose File" in html

    def test_input_file_default_button_label(self) -> None:
        """Test input_file default button label is 'Browse...'."""
        result = input_file("file_id", "Upload")
        html = str(result)

        assert "Browse..." in html

    def test_input_file_placeholder(self) -> None:
        """Test input_file with custom placeholder."""
        result = input_file("file_id", "Upload", placeholder="Select a file")
        html = str(result)

        assert 'placeholder="Select a file"' in html

    def test_input_file_default_placeholder(self) -> None:
        """Test input_file default placeholder."""
        result = input_file("file_id", "Upload")
        html = str(result)

        assert 'placeholder="No file selected"' in html

    def test_input_file_capture_environment(self) -> None:
        """Test input_file with capture='environment'."""
        result = input_file("file_id", "Upload", capture="environment")
        html = str(result)

        assert 'capture="environment"' in html

    def test_input_file_capture_user(self) -> None:
        """Test input_file with capture='user'."""
        result = input_file("file_id", "Upload", capture="user")
        html = str(result)

        assert 'capture="user"' in html

    def test_input_file_with_all_parameters(self) -> None:
        """Test input_file with all parameters."""
        result = input_file(
            "full_file_id",
            "Full File Upload",
            multiple=True,
            accept=[".jpg", ".png", ".gif"],
            width="500px",
            button_label="Select Images",
            placeholder="No images selected",
            capture="environment",
        )
        html = str(result)

        assert 'id="full_file_id"' in html
        assert "Full File Upload" in html
        assert 'multiple="multiple"' in html
        assert 'accept=".jpg,.png,.gif"' in html
        assert "width:500px" in html
        assert "Select Images" in html
        assert 'placeholder="No images selected"' in html
        assert 'capture="environment"' in html

    def test_input_file_form_group_class(self) -> None:
        """Test that container has form-group class."""
        result = input_file("file_id", "Upload")
        html = str(result)

        assert "form-group" in html
        assert "shiny-input-container" in html

    def test_input_file_shiny_input_file_class(self) -> None:
        """Test input_file has shiny-input-file class."""
        result = input_file("file_id", "Upload")
        html = str(result)

        assert "shiny-input-file" in html

    def test_input_file_progress_bar(self) -> None:
        """Test input_file includes progress bar."""
        result = input_file("file_id", "Upload")
        html = str(result)

        assert "progress-bar" in html
        assert "shiny-file-input-progress" in html

    def test_input_file_progress_bar_id(self) -> None:
        """Test input_file progress bar has correct id."""
        result = input_file("file_id", "Upload")
        html = str(result)

        assert 'id="file_id_progress"' in html

    def test_input_file_html_label(self) -> None:
        """Test input_file with HTML label."""
        from htmltools import tags

        label = tags.strong("Bold Upload")
        result = input_file("file_id", label)
        html = str(result)

        assert "<strong>Bold Upload</strong>" in html

    def test_input_file_empty_label(self) -> None:
        """Test input_file with empty label."""
        result = input_file("file_id", "")
        html = str(result)

        assert 'id="file_id"' in html

    def test_input_file_btn_class(self) -> None:
        """Test input_file button has correct classes."""
        result = input_file("file_id", "Upload")
        html = str(result)

        assert "btn btn-default btn-file" in html

    def test_input_file_input_group(self) -> None:
        """Test input_file has input-group wrapper."""
        result = input_file("file_id", "Upload")
        html = str(result)

        assert "input-group" in html

    def test_input_file_accept_multiple_types(self) -> None:
        """Test input_file with multiple accept types."""
        result = input_file(
            "file_id",
            "Upload",
            accept=["image/*", "application/pdf", ".docx"],
        )
        html = str(result)

        assert 'accept="image/*,application/pdf,.docx"' in html

    def test_input_file_readonly_text_input(self) -> None:
        """Test input_file has readonly text input for filename display."""
        result = input_file("file_id", "Upload")
        html = str(result)

        assert 'readonly="readonly"' in html
