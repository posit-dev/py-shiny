"""Tests for shiny.experimental.ui._card module."""

import io
from pathlib import Path

import pytest

from shiny.experimental.ui._card import card_image


class TestCardImage:
    """Tests for card_image function."""

    def test_card_image_with_none_file(self):
        """card_image should work with file=None and src provided."""
        result = card_image(None, src="https://example.com/image.jpg")
        assert result is not None

    def test_card_image_with_file_path(self, tmp_path: Path) -> None:
        """card_image should work with a file path."""
        # Create a simple image file (1x1 PNG)
        img_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
            b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        img_file = tmp_path / "test.png"
        img_file.write_bytes(img_data)

        result = card_image(str(img_file))
        assert result is not None

    def test_card_image_with_path_object(self, tmp_path: Path) -> None:
        """card_image should work with Path object."""
        img_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
            b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        img_file = tmp_path / "test.png"
        img_file.write_bytes(img_data)

        result = card_image(img_file)
        assert result is not None

    def test_card_image_with_bytes_io(self):
        """card_image should work with BytesIO."""
        img_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
            b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        buffer = io.BytesIO(img_data)
        result = card_image(buffer, mime_type="image/png")
        assert result is not None

    def test_card_image_bytes_io_requires_mime_type(self):
        """card_image with BytesIO should require mime_type."""
        img_data = b"\x89PNG"
        buffer = io.BytesIO(img_data)
        with pytest.raises(ValueError, match="mime_type"):
            card_image(buffer)

    def test_card_image_with_href(self, tmp_path: Path) -> None:
        """card_image should accept href parameter."""
        img_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
            b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        img_file = tmp_path / "test.png"
        img_file.write_bytes(img_data)

        result = card_image(str(img_file), href="https://example.com")
        assert result is not None

    def test_card_image_border_radius_options(self, tmp_path: Path) -> None:
        """card_image should accept different border_radius options."""
        img_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
            b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        img_file = tmp_path / "test.png"
        img_file.write_bytes(img_data)

        for radius in ["top", "bottom", "all", "none"]:
            result = card_image(str(img_file), border_radius=radius)
            assert result is not None

    def test_card_image_with_height(self, tmp_path: Path) -> None:
        """card_image should accept height parameter."""
        img_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
            b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        img_file = tmp_path / "test.png"
        img_file.write_bytes(img_data)

        result = card_image(str(img_file), height="200px")
        assert result is not None

    def test_card_image_with_width(self, tmp_path: Path) -> None:
        """card_image should accept width parameter."""
        img_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
            b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        img_file = tmp_path / "test.png"
        img_file.write_bytes(img_data)

        result = card_image(str(img_file), width="100%")
        assert result is not None

    def test_card_image_fill_false(self, tmp_path: Path) -> None:
        """card_image should accept fill=False."""
        img_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
            b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        img_file = tmp_path / "test.png"
        img_file.write_bytes(img_data)

        result = card_image(str(img_file), fill=False)
        assert result is not None

    def test_card_image_with_class(self, tmp_path: Path) -> None:
        """card_image should accept class_ parameter."""
        img_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
            b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        img_file = tmp_path / "test.png"
        img_file.write_bytes(img_data)

        result = card_image(str(img_file), class_="my-image")
        assert result is not None

    def test_card_image_no_container(self, tmp_path: Path) -> None:
        """card_image should work with container=None."""
        img_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
            b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        img_file = tmp_path / "test.png"
        img_file.write_bytes(img_data)

        result = card_image(str(img_file), container=None)
        assert result is not None
