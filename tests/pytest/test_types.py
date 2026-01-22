"""Tests for shiny.types module."""

from __future__ import annotations

import pytest


class TestMissingType:
    """Tests for MISSING and MISSING_TYPE sentinel values."""

    def test_missing_type_exists(self):
        """MISSING_TYPE class should exist."""
        from shiny.types import MISSING_TYPE

        assert MISSING_TYPE is not None

    def test_missing_singleton(self):
        """MISSING should be an instance of MISSING_TYPE."""
        from shiny.types import MISSING, MISSING_TYPE

        assert isinstance(MISSING, MISSING_TYPE)

    def test_missing_identity(self):
        """MISSING should maintain identity across imports."""
        from shiny.types import MISSING as MISSING1
        from shiny.types import MISSING as MISSING2

        assert MISSING1 is MISSING2

    def test_missing_is_not_none(self):
        """MISSING should not be None."""
        from shiny.types import MISSING

        assert MISSING is not None


class TestFileInfo:
    """Tests for FileInfo TypedDict."""

    def test_file_info_structure(self):
        """FileInfo should accept valid file information."""
        from shiny.types import FileInfo

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


class TestImgData:
    """Tests for ImgData TypedDict."""

    def test_img_data_required_fields(self):
        """ImgData should work with only required fields."""
        from shiny.types import ImgData

        img_data: ImgData = {"src": "data:image/png;base64,abc123"}
        assert img_data["src"] == "data:image/png;base64,abc123"

    def test_img_data_all_fields(self):
        """ImgData should accept all optional fields."""
        from shiny.types import ImgData

        img_data: ImgData = {
            "src": "image.png",
            "width": "100px",
            "height": 200,
            "alt": "Test image",
            "style": "border: 1px solid black;",
        }
        assert img_data["src"] == "image.png"
        assert img_data["width"] == "100px"
        assert img_data["height"] == 200
        assert img_data["alt"] == "Test image"


class TestExceptions:
    """Tests for custom exception classes."""

    def test_safe_exception_inheritance(self):
        """SafeException should inherit from Exception."""
        from shiny.types import SafeException

        assert issubclass(SafeException, Exception)

    def test_safe_exception_raise(self):
        """SafeException should be raisable with a message."""
        from shiny.types import SafeException

        with pytest.raises(SafeException) as exc_info:
            raise SafeException("Test safe error")
        assert "Test safe error" in str(exc_info.value)

    def test_silent_exception_inheritance(self):
        """SilentException should inherit from Exception."""
        from shiny.types import SilentException

        assert issubclass(SilentException, Exception)

    def test_silent_exception_raise(self):
        """SilentException should be raisable."""
        from shiny.types import SilentException

        with pytest.raises(SilentException):
            raise SilentException()

    def test_silent_cancel_output_exception_inheritance(self):
        """SilentCancelOutputException should inherit from Exception."""
        from shiny.types import SilentCancelOutputException

        assert issubclass(SilentCancelOutputException, Exception)


class TestNotifyException:
    """Tests for NotifyException class."""

    def test_notify_exception_default_values(self):
        """NotifyException should have correct default values."""
        from shiny.types import NotifyException

        exc = NotifyException("Test message")
        assert exc.sanitize is True
        assert exc.close is False

    def test_notify_exception_custom_values(self):
        """NotifyException should accept custom sanitize and close values."""
        from shiny.types import NotifyException

        exc = NotifyException("Test message", sanitize=False, close=True)
        assert exc.sanitize is False
        assert exc.close is True

    def test_notify_exception_message(self):
        """NotifyException should preserve the message."""
        from shiny.types import NotifyException

        exc = NotifyException("Custom error message")
        assert "Custom error message" in str(exc)


class TestActionButtonValue:
    """Tests for ActionButtonValue class."""

    def test_action_button_value_is_int(self):
        """ActionButtonValue should be an int subclass."""
        from shiny.types import ActionButtonValue

        assert issubclass(ActionButtonValue, int)

    def test_action_button_value_creation(self):
        """ActionButtonValue should be creatable from an integer."""
        from shiny.types import ActionButtonValue

        value = ActionButtonValue(5)
        assert value == 5
        assert isinstance(value, int)


class TestCoordmapTypes:
    """Tests for coordinate map related TypedDicts."""

    def test_coordmap_dims(self):
        """CoordmapDims should accept width and height."""
        from shiny.types import CoordmapDims

        dims: CoordmapDims = {"width": 800.0, "height": 600.0}
        assert dims["width"] == 800.0
        assert dims["height"] == 600.0

    def test_coordmap_panel_log(self):
        """CoordmapPanelLog should accept x and y log values."""
        from shiny.types import CoordmapPanelLog

        log: CoordmapPanelLog = {"x": None, "y": 10.0}
        assert log["x"] is None
        assert log["y"] == 10.0

    def test_coordmap_panel_domain(self):
        """CoordmapPanelDomain should define domain boundaries."""
        from shiny.types import CoordmapPanelDomain

        domain: CoordmapPanelDomain = {
            "left": 0.0,
            "right": 100.0,
            "bottom": 0.0,
            "top": 50.0,
        }
        assert domain["left"] == 0.0
        assert domain["right"] == 100.0

    def test_coordmap_panel_range(self):
        """CoordmapPanelRange should define range boundaries."""
        from shiny.types import CoordmapPanelRange

        range_val: CoordmapPanelRange = {
            "left": 10.0,
            "right": 790.0,
            "bottom": 590.0,
            "top": 10.0,
        }
        assert range_val["left"] == 10.0

    def test_coord_xy(self):
        """CoordXY should hold x and y coordinates."""
        from shiny.types import CoordXY

        coord: CoordXY = {"x": 150.5, "y": 200.3}
        assert coord["x"] == 150.5
        assert coord["y"] == 200.3


class TestCoordInfo:
    """Tests for CoordInfo TypedDict (click/hover data)."""

    def test_coord_info_structure(self):
        """CoordInfo should contain all required coordinate info."""
        from shiny.types import CoordInfo

        coord_info: CoordInfo = {
            "x": 50.0,
            "y": 100.0,
            "coords_css": {"x": 150.0, "y": 200.0},
            "coords_img": {"x": 50.0, "y": 100.0},
            "img_css_ratio": {"x": 3.0, "y": 2.0},
            "mapping": {"x": "mpg", "y": "hp"},
            "domain": {"left": 0.0, "right": 35.0, "bottom": 0.0, "top": 400.0},
            "range": {"left": 50.0, "right": 750.0, "bottom": 550.0, "top": 50.0},
            "log": {"x": None, "y": None},
        }
        assert coord_info["x"] == 50.0
        assert coord_info["mapping"]["x"] == "mpg"


class TestBrushInfo:
    """Tests for BrushInfo TypedDict (brush selection data)."""

    def test_brush_info_structure(self):
        """BrushInfo should contain brush boundary information."""
        from shiny.types import BrushInfo

        brush_info: BrushInfo = {
            "xmin": 10.0,
            "xmax": 30.0,
            "ymin": 50.0,
            "ymax": 200.0,
            "coords_css": {"x": 150.0, "y": 200.0},
            "coords_img": {"x": 50.0, "y": 100.0},
            "img_css_ratio": {"x": 3.0, "y": 2.0},
            "mapping": {"x": "mpg", "y": "hp"},
            "domain": {"left": 0.0, "right": 35.0, "bottom": 0.0, "top": 400.0},
            "range": {"left": 50.0, "right": 750.0, "bottom": 550.0, "top": 50.0},
            "log": {"x": None, "y": None},
            "direction": "xy",
        }
        assert brush_info["xmin"] == 10.0
        assert brush_info["xmax"] == 30.0
        assert brush_info["direction"] == "xy"


class TestJsonifiable:
    """Tests for Jsonifiable type alias."""

    def test_jsonifiable_imports(self):
        """Jsonifiable type should be importable."""
        from shiny.types import Jsonifiable, JsonifiableDict

        # These are type aliases, so we just verify they can be imported
        assert Jsonifiable is not None
        assert JsonifiableDict is not None


class TestListOrTuple:
    """Tests for ListOrTuple type alias."""

    def test_list_or_tuple_import(self):
        """ListOrTuple should be importable."""
        from shiny.types import ListOrTuple

        assert ListOrTuple is not None


class TestModuleExports:
    """Tests for module __all__ exports."""

    def test_all_exports_exist(self):
        """All items in __all__ should be importable."""
        from shiny import types

        for name in types.__all__:
            assert hasattr(types, name), f"{name} not found in shiny.types"
            obj = getattr(types, name)
            assert obj is not None, f"{name} is None"

    def test_expected_exports(self):
        """Expected public types should be exported."""
        from shiny.types import (
            MISSING,
            MISSING_TYPE,
            FileInfo,
            ImgData,
            Jsonifiable,
            SafeException,
            SilentCancelOutputException,
            SilentException,
        )

        # Just verify they're all importable
        assert all(
            [
                MISSING,
                MISSING_TYPE,
                Jsonifiable,
                FileInfo,
                ImgData,
                SafeException,
                SilentException,
                SilentCancelOutputException,
            ]
        )
