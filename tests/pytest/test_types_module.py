"""Tests for shiny.types module."""

import pytest

from shiny.types import (
    MISSING,
    MISSING_TYPE,
    FileInfo,
    ImgData,
    SafeException,
    SilentCancelOutputException,
    SilentException,
)


class TestMISSING:
    """Tests for MISSING sentinel value."""

    def test_missing_type_exists(self):
        """Test that MISSING_TYPE class exists."""
        assert MISSING_TYPE is not None

    def test_missing_instance_exists(self):
        """Test that MISSING instance exists."""
        assert MISSING is not None

    def test_missing_is_instance_of_missing_type(self):
        """Test that MISSING is an instance of MISSING_TYPE."""
        assert isinstance(MISSING, MISSING_TYPE)


class TestFileInfo:
    """Tests for FileInfo TypedDict."""

    def test_file_info_creation(self):
        """Test creating FileInfo."""
        info: FileInfo = {
            "name": "test.txt",
            "size": 1024,
            "type": "text/plain",
            "datapath": "/tmp/test.txt",
        }

        assert info["name"] == "test.txt"
        assert info["size"] == 1024
        assert info["type"] == "text/plain"
        assert info["datapath"] == "/tmp/test.txt"


class TestImgData:
    """Tests for ImgData TypedDict."""

    def test_img_data_basic(self):
        """Test creating basic ImgData."""
        img: ImgData = {"src": "data:image/png;base64,..."}

        assert img["src"] == "data:image/png;base64,..."

    def test_img_data_with_dimensions(self):
        """Test creating ImgData with dimensions."""
        img: ImgData = {
            "src": "image.png",
            "width": 400,
            "height": 300,
        }

        assert img["width"] == 400
        assert img["height"] == 300

    def test_img_data_with_alt(self):
        """Test creating ImgData with alt text."""
        img: ImgData = {
            "src": "image.png",
            "alt": "An example image",
        }

        assert img["alt"] == "An example image"


class TestSafeException:
    """Tests for SafeException class."""

    def test_safe_exception_creation(self):
        """Test creating SafeException."""
        exc = SafeException("Safe error message")
        assert str(exc) == "Safe error message"

    def test_safe_exception_is_exception(self):
        """Test SafeException is an Exception."""
        exc = SafeException("Test")
        assert isinstance(exc, Exception)

    def test_safe_exception_raise(self):
        """Test raising SafeException."""
        with pytest.raises(SafeException):
            raise SafeException("Test error")


class TestSilentException:
    """Tests for SilentException class."""

    def test_silent_exception_creation(self):
        """Test creating SilentException."""
        exc = SilentException()
        assert exc is not None

    def test_silent_exception_is_exception(self):
        """Test SilentException is an Exception."""
        exc = SilentException()
        assert isinstance(exc, Exception)

    def test_silent_exception_raise(self):
        """Test raising SilentException."""
        with pytest.raises(SilentException):
            raise SilentException()


class TestSilentCancelOutputException:
    """Tests for SilentCancelOutputException class."""

    def test_silent_cancel_output_exception_creation(self):
        """Test creating SilentCancelOutputException."""
        exc = SilentCancelOutputException()
        assert exc is not None

    def test_silent_cancel_output_exception_is_exception(self):
        """Test SilentCancelOutputException is an Exception."""
        exc = SilentCancelOutputException()
        assert isinstance(exc, Exception)

    def test_silent_cancel_output_exception_raise(self):
        """Test raising SilentCancelOutputException."""
        with pytest.raises(SilentCancelOutputException):
            raise SilentCancelOutputException()
