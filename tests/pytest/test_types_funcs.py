"""Tests for shiny.types module"""

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


class TestMissingSentinel:
    """Test MISSING sentinel value"""

    def test_missing_is_missing_type(self):
        """Test that MISSING is instance of MISSING_TYPE"""
        assert isinstance(MISSING, MISSING_TYPE)

    def test_missing_type_instantiation(self):
        """Test that MISSING_TYPE can be instantiated"""
        instance = MISSING_TYPE()
        assert isinstance(instance, MISSING_TYPE)

    def test_missing_identity(self):
        """Test that MISSING is a singleton-like sentinel"""
        # MISSING should be the same object when imported
        from shiny.types import MISSING as MISSING2

        assert MISSING is MISSING2

    def test_missing_type_truthiness(self):
        """Test MISSING_TYPE instances are truthy by default"""
        instance = MISSING_TYPE()
        # Default objects are truthy
        assert bool(instance)


class TestFileInfo:
    """Test FileInfo TypedDict"""

    def test_file_info_creation(self):
        """Test creating a FileInfo dict"""
        file_info: FileInfo = {
            "name": "test.csv",
            "size": 1024,
            "type": "text/csv",
            "datapath": "/tmp/test.csv",
        }
        assert file_info["name"] == "test.csv"
        assert file_info["size"] == 1024
        assert file_info["type"] == "text/csv"
        assert file_info["datapath"] == "/tmp/test.csv"

    def test_file_info_required_keys(self):
        """Test that FileInfo has expected keys"""
        file_info: FileInfo = {
            "name": "file.txt",
            "size": 100,
            "type": "text/plain",
            "datapath": "/path/to/file",
        }
        assert "name" in file_info
        assert "size" in file_info
        assert "type" in file_info
        assert "datapath" in file_info


class TestImgData:
    """Test ImgData TypedDict"""

    def test_img_data_minimal(self):
        """Test creating ImgData with only required fields"""
        img: ImgData = {"src": "data:image/png;base64,xxx"}
        assert img["src"] == "data:image/png;base64,xxx"

    def test_img_data_with_dimensions(self):
        """Test creating ImgData with dimensions"""
        img: ImgData = {"src": "image.png", "width": 400, "height": 300}
        assert img["src"] == "image.png"
        assert img["width"] == 400
        assert img["height"] == 300

    def test_img_data_with_string_dimensions(self):
        """Test creating ImgData with string dimensions"""
        img: ImgData = {"src": "image.png", "width": "100%", "height": "auto"}
        assert img["width"] == "100%"
        assert img["height"] == "auto"

    def test_img_data_with_alt(self):
        """Test creating ImgData with alt text"""
        img: ImgData = {"src": "image.png", "alt": "An image"}
        assert img["alt"] == "An image"

    def test_img_data_with_style(self):
        """Test creating ImgData with style"""
        img: ImgData = {"src": "image.png", "style": "border: 1px solid black;"}
        assert img["style"] == "border: 1px solid black;"

    def test_img_data_full(self):
        """Test creating ImgData with all optional fields"""
        img: ImgData = {
            "src": "image.png",
            "width": 640,
            "height": 480,
            "alt": "Test image",
            "style": "max-width: 100%;",
        }
        assert len(img) == 5


class TestSafeException:
    """Test SafeException class"""

    def test_safe_exception_is_exception(self):
        """Test that SafeException is an Exception"""
        exc = SafeException("Test error")
        assert isinstance(exc, Exception)

    def test_safe_exception_message(self):
        """Test SafeException message"""
        exc = SafeException("Safe error message")
        assert str(exc) == "Safe error message"

    def test_safe_exception_raise(self):
        """Test raising SafeException"""
        with pytest.raises(SafeException) as exc_info:
            raise SafeException("Test")
        assert str(exc_info.value) == "Test"


class TestSilentException:
    """Test SilentException class"""

    def test_silent_exception_is_exception(self):
        """Test that SilentException is an Exception"""
        exc = SilentException()
        assert isinstance(exc, Exception)

    def test_silent_exception_with_message(self):
        """Test SilentException with message"""
        exc = SilentException("Silent error")
        assert str(exc) == "Silent error"

    def test_silent_exception_raise(self):
        """Test raising SilentException"""
        with pytest.raises(SilentException):
            raise SilentException()


class TestSilentCancelOutputException:
    """Test SilentCancelOutputException class"""

    def test_silent_cancel_is_exception(self):
        """Test that SilentCancelOutputException is an Exception"""
        exc = SilentCancelOutputException()
        assert isinstance(exc, Exception)

    def test_silent_cancel_with_message(self):
        """Test SilentCancelOutputException with message"""
        exc = SilentCancelOutputException("Cancel output")
        assert str(exc) == "Cancel output"

    def test_silent_cancel_raise(self):
        """Test raising SilentCancelOutputException"""
        with pytest.raises(SilentCancelOutputException):
            raise SilentCancelOutputException()

    def test_silent_cancel_not_subclass_of_silent(self):
        """Test SilentCancelOutputException is separate from SilentException"""
        # They're separate exception types, not a subclass hierarchy
        exc = SilentCancelOutputException()
        assert isinstance(exc, Exception)


class TestSilentOperationInProgressException:
    """Test SilentOperationInProgressException class"""

    def test_import(self):
        """Test that SilentOperationInProgressException can be imported"""
        from shiny.types import SilentOperationInProgressException

        exc = SilentOperationInProgressException()
        assert isinstance(exc, Exception)

    def test_is_subclass_of_silent(self):
        """Test SilentOperationInProgressException is subclass of SilentException"""
        from shiny.types import SilentOperationInProgressException

        exc = SilentOperationInProgressException()
        assert isinstance(exc, SilentException)


class TestNotifyException:
    """Test NotifyException class"""

    def test_import(self):
        """Test that NotifyException can be imported"""
        from shiny.types import NotifyException

        exc = NotifyException("message")
        assert isinstance(exc, Exception)

    def test_default_values(self):
        """Test NotifyException default values"""
        from shiny.types import NotifyException

        exc = NotifyException("Test message")
        assert exc.sanitize is True
        assert exc.close is False

    def test_custom_values(self):
        """Test NotifyException with custom values"""
        from shiny.types import NotifyException

        exc = NotifyException("Error", sanitize=False, close=True)
        assert exc.sanitize is False
        assert exc.close is True

    def test_message(self):
        """Test NotifyException message"""
        from shiny.types import NotifyException

        exc = NotifyException("Custom error message")
        assert str(exc) == "('Custom error message', True, False)"


class TestActionButtonValue:
    """Test ActionButtonValue class"""

    def test_import(self):
        """Test that ActionButtonValue can be imported"""
        from shiny.types import ActionButtonValue

        val = ActionButtonValue(5)
        assert isinstance(val, int)

    def test_value(self):
        """Test ActionButtonValue stores integer value"""
        from shiny.types import ActionButtonValue

        val = ActionButtonValue(10)
        assert val == 10

    def test_arithmetic(self):
        """Test ActionButtonValue supports int arithmetic"""
        from shiny.types import ActionButtonValue

        val = ActionButtonValue(5)
        assert val + 3 == 8
        assert val * 2 == 10
