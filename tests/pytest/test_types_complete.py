"""Comprehensive tests for shiny.types module to achieve 100% coverage."""

from __future__ import annotations

import pytest

# Import all types at module level to ensure coverage sees them
from shiny import types as shiny_types


class TestMissingTypeComplete:
    """Complete tests for MISSING and MISSING_TYPE."""

    def test_missing_type_class_exists(self):
        """MISSING_TYPE class should exist and be importable."""
        from shiny.types import MISSING_TYPE

        assert MISSING_TYPE is not None
        assert isinstance(MISSING_TYPE, type)

    def test_missing_instance_creation(self):
        """MISSING should be instance of MISSING_TYPE."""
        from shiny.types import MISSING, MISSING_TYPE

        assert isinstance(MISSING, MISSING_TYPE)

    def test_missing_singleton_behavior(self):
        """MISSING should maintain singleton behavior."""
        from shiny.types import MISSING as M1
        from shiny.types import MISSING as M2

        assert M1 is M2

    def test_missing_not_equal_to_none(self):
        """MISSING should not be equal to None."""
        from shiny.types import MISSING

        assert MISSING is not None
        assert MISSING != None  # noqa: E711

    def test_deprecated_sentinel(self):
        """DEPRECATED sentinel should exist and be MISSING_TYPE."""
        from shiny.types import DEPRECATED, MISSING_TYPE

        assert isinstance(DEPRECATED, MISSING_TYPE)

    def test_missing_type_instantiation(self):
        """MISSING_TYPE should be instantiable."""
        from shiny.types import MISSING_TYPE

        instance = MISSING_TYPE()
        assert isinstance(instance, MISSING_TYPE)


class TestFileInfoComplete:
    """Complete tests for FileInfo TypedDict."""

    def test_file_info_all_required_fields(self):
        """FileInfo should have all required fields."""
        from shiny.types import FileInfo

        file_info: FileInfo = {
            "name": "document.pdf",
            "size": 2048,
            "type": "application/pdf",
            "datapath": "/uploads/document.pdf",
        }
        assert file_info["name"] == "document.pdf"
        assert file_info["size"] == 2048
        assert file_info["type"] == "application/pdf"
        assert file_info["datapath"] == "/uploads/document.pdf"

    def test_file_info_numeric_size(self):
        """FileInfo size should accept integers."""
        from shiny.types import FileInfo

        file_info: FileInfo = {
            "name": "large.zip",
            "size": 10485760,
            "type": "application/zip",
            "datapath": "/tmp/large.zip",
        }
        assert isinstance(file_info["size"], int)
        assert file_info["size"] > 0

    def test_file_info_various_mime_types(self):
        """FileInfo should accept various MIME types."""
        from shiny.types import FileInfo

        types_to_test = [
            "text/plain",
            "image/jpeg",
            "application/json",
            "text/csv",
            "video/mp4",
        ]

        for mime_type in types_to_test:
            file_info: FileInfo = {
                "name": f"file.{mime_type.split('/')[-1]}",
                "size": 1024,
                "type": mime_type,
                "datapath": f"/tmp/file.{mime_type.split('/')[-1]}",
            }
            assert file_info["type"] == mime_type


class TestImgDataComplete:
    """Complete tests for ImgData TypedDict."""

    def test_img_data_only_src(self):
        """ImgData should work with only src (required field)."""
        from shiny.types import ImgData

        img: ImgData = {"src": "/images/photo.jpg"}
        assert img["src"] == "/images/photo.jpg"

    def test_img_data_with_width_string(self):
        """ImgData width should accept string values."""
        from shiny.types import ImgData

        img: ImgData = {"src": "img.png", "width": "50%"}
        assert img["width"] == "50%"

    def test_img_data_with_width_float(self):
        """ImgData width should accept float values."""
        from shiny.types import ImgData

        img: ImgData = {"src": "img.png", "width": 150.5}
        assert img["width"] == 150.5

    def test_img_data_with_height_string(self):
        """ImgData height should accept string values."""
        from shiny.types import ImgData

        img: ImgData = {"src": "img.png", "height": "200px"}
        assert img["height"] == "200px"

    def test_img_data_with_height_float(self):
        """ImgData height should accept float values."""
        from shiny.types import ImgData

        img: ImgData = {"src": "img.png", "height": 300.0}
        assert img["height"] == 300.0

    def test_img_data_with_alt_text(self):
        """ImgData should accept alt text."""
        from shiny.types import ImgData

        img: ImgData = {"src": "logo.png", "alt": "Company Logo"}
        assert img["alt"] == "Company Logo"

    def test_img_data_with_style(self):
        """ImgData should accept CSS style string."""
        from shiny.types import ImgData

        img: ImgData = {"src": "bg.jpg", "style": "opacity: 0.8; border-radius: 5px;"}
        assert "opacity" in img["style"]  # type: ignore
        assert "border-radius" in img["style"]  # type: ignore

    def test_img_data_with_coordmap(self):
        """ImgData should accept coordmap."""
        from shiny.types import ImgData

        coordmap_data = {"panels": [], "dims": {"width": 100, "height": 100}}  # type: ignore[var-annotated]
        img: ImgData = {"src": "plot.png", "coordmap": coordmap_data}
        assert img["coordmap"] == coordmap_data

    def test_img_data_all_fields_combined(self):
        """ImgData should accept all fields together."""
        from shiny.types import ImgData

        img: ImgData = {
            "src": "complete.png",
            "width": 640,
            "height": "480px",
            "alt": "Complete image",
            "style": "border: 1px solid #ccc;",
            "coordmap": {"test": "data"},
        }
        assert len(img) == 6


class TestSafeExceptionComplete:
    """Complete tests for SafeException."""

    def test_safe_exception_is_exception_subclass(self):
        """SafeException should be a subclass of Exception."""
        from shiny.types import SafeException

        assert issubclass(SafeException, Exception)

    def test_safe_exception_can_be_raised(self):
        """SafeException should be raisable."""
        from shiny.types import SafeException

        with pytest.raises(SafeException):
            raise SafeException("Error message")

    def test_safe_exception_with_message(self):
        """SafeException should preserve error message."""
        from shiny.types import SafeException

        msg = "This is a safe error"
        with pytest.raises(SafeException) as exc:
            raise SafeException(msg)
        assert msg in str(exc.value)

    def test_safe_exception_empty_message(self):
        """SafeException should work with empty message."""
        from shiny.types import SafeException

        with pytest.raises(SafeException):
            raise SafeException()

    def test_safe_exception_inheritable(self):
        """SafeException should be inheritable."""
        from shiny.types import SafeException

        class CustomSafeException(SafeException):
            pass

        assert issubclass(CustomSafeException, SafeException)
        with pytest.raises(CustomSafeException):
            raise CustomSafeException("Custom error")


class TestSilentExceptionComplete:
    """Complete tests for SilentException."""

    def test_silent_exception_is_exception_subclass(self):
        """SilentException should be a subclass of Exception."""
        from shiny.types import SilentException

        assert issubclass(SilentException, Exception)

    def test_silent_exception_can_be_raised(self):
        """SilentException should be raisable."""
        from shiny.types import SilentException

        with pytest.raises(SilentException):
            raise SilentException()

    def test_silent_exception_with_message(self):
        """SilentException should accept a message."""
        from shiny.types import SilentException

        with pytest.raises(SilentException) as exc:
            raise SilentException("Silent error")
        assert "Silent error" in str(exc.value)


class TestSilentCancelOutputExceptionComplete:
    """Complete tests for SilentCancelOutputException."""

    def test_silent_cancel_is_exception_subclass(self):
        """SilentCancelOutputException should be Exception subclass."""
        from shiny.types import SilentCancelOutputException

        assert issubclass(SilentCancelOutputException, Exception)

    def test_silent_cancel_can_be_raised(self):
        """SilentCancelOutputException should be raisable."""
        from shiny.types import SilentCancelOutputException

        with pytest.raises(SilentCancelOutputException):
            raise SilentCancelOutputException()

    def test_silent_cancel_with_message(self):
        """SilentCancelOutputException should accept a message."""
        from shiny.types import SilentCancelOutputException

        with pytest.raises(SilentCancelOutputException) as exc:
            raise SilentCancelOutputException("Cancelled")
        assert "Cancelled" in str(exc.value)


class TestSilentOperationInProgressException:
    """Tests for SilentOperationInProgressException."""

    def test_is_silent_exception_subclass(self):
        """SilentOperationInProgressException should inherit from SilentException."""
        from shiny.types import SilentException, SilentOperationInProgressException

        assert issubclass(SilentOperationInProgressException, SilentException)

    def test_can_be_raised(self):
        """SilentOperationInProgressException should be raisable."""
        from shiny.types import SilentOperationInProgressException

        with pytest.raises(SilentOperationInProgressException):
            raise SilentOperationInProgressException()

    def test_with_message(self):
        """SilentOperationInProgressException should accept a message."""
        from shiny.types import SilentOperationInProgressException

        with pytest.raises(SilentOperationInProgressException) as exc:
            raise SilentOperationInProgressException("Operation in progress")
        assert "Operation in progress" in str(exc.value)


class TestNotifyException:
    """Tests for NotifyException."""

    def test_is_exception_subclass(self):
        """NotifyException should be Exception subclass."""
        from shiny.types import NotifyException

        assert issubclass(NotifyException, Exception)

    def test_can_be_raised_with_message(self):
        """NotifyException should be raisable with message."""
        from shiny.types import NotifyException

        with pytest.raises(NotifyException) as exc:
            raise NotifyException("Notification message")
        assert "Notification message" in str(exc.value)

    def test_default_sanitize_true(self):
        """NotifyException should have sanitize=True by default."""
        from shiny.types import NotifyException

        exc = NotifyException("Test")
        assert exc.sanitize is True

    def test_default_close_false(self):
        """NotifyException should have close=False by default."""
        from shiny.types import NotifyException

        exc = NotifyException("Test")
        assert exc.close is False

    def test_custom_sanitize_false(self):
        """NotifyException should accept sanitize=False."""
        from shiny.types import NotifyException

        exc = NotifyException("Test", sanitize=False)
        assert exc.sanitize is False

    def test_custom_close_true(self):
        """NotifyException should accept close=True."""
        from shiny.types import NotifyException

        exc = NotifyException("Test", close=True)
        assert exc.close is True

    def test_all_params(self):
        """NotifyException should accept all parameters."""
        from shiny.types import NotifyException

        exc = NotifyException("Test message", sanitize=False, close=True)
        assert "Test message" in str(exc)
        assert exc.sanitize is False
        assert exc.close is True


class TestActionButtonValue:
    """Tests for ActionButtonValue."""

    def test_is_int_subclass(self):
        """ActionButtonValue should be int subclass."""
        from shiny.types import ActionButtonValue

        assert issubclass(ActionButtonValue, int)

    def test_can_be_instantiated(self):
        """ActionButtonValue should be instantiable."""
        from shiny.types import ActionButtonValue

        value = ActionButtonValue(5)
        assert value == 5
        assert isinstance(value, int)

    def test_arithmetic_operations(self):
        """ActionButtonValue should support arithmetic operations."""
        from shiny.types import ActionButtonValue

        value = ActionButtonValue(10)
        assert value + 5 == 15
        assert value * 2 == 20


class TestModuleExports:
    """Tests for module __all__ exports."""

    def test_all_exports_exist(self):
        """All items in __all__ should be importable."""
        for name in shiny_types.__all__:
            assert hasattr(shiny_types, name)

    def test_all_is_tuple(self):
        """__all__ should be a tuple."""
        assert isinstance(shiny_types.__all__, tuple)
