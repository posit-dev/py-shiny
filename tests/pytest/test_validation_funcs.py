"""Tests for shiny._validation module."""

import pytest

from shiny._validation import req
from shiny.types import (
    SilentCancelOutputException,
    SilentException,
    SilentOperationInProgressException,
)


class TestReq:
    """Tests for req function."""

    def test_req_truthy_value(self) -> None:
        """Test req with truthy value passes through."""
        result = req(True)
        assert result is True

    def test_req_truthy_string(self) -> None:
        """Test req with truthy string passes through."""
        result = req("hello")
        assert result == "hello"

    def test_req_truthy_number(self) -> None:
        """Test req with truthy number passes through."""
        result = req(42)
        assert result == 42

    def test_req_truthy_list(self) -> None:
        """Test req with truthy list passes through."""
        result = req([1, 2, 3])
        assert result == [1, 2, 3]

    def test_req_falsy_none_raises(self) -> None:
        """Test req with None raises SilentException."""
        with pytest.raises(SilentException):
            req(None)

    def test_req_falsy_false_raises(self) -> None:
        """Test req with False raises SilentException."""
        with pytest.raises(SilentException):
            req(False)

    def test_req_falsy_zero_raises(self) -> None:
        """Test req with 0 raises SilentException."""
        with pytest.raises(SilentException):
            req(0)

    def test_req_falsy_empty_string_raises(self) -> None:
        """Test req with empty string raises SilentException."""
        with pytest.raises(SilentException):
            req("")

    def test_req_falsy_empty_list_raises(self) -> None:
        """Test req with empty list raises SilentException."""
        with pytest.raises(SilentException):
            req([])

    def test_req_cancel_output_true(self) -> None:
        """Test req with cancel_output=True raises SilentCancelOutputException."""
        with pytest.raises(SilentCancelOutputException):
            req(None, cancel_output=True)

    def test_req_cancel_output_progress(self) -> None:
        """Test req with cancel_output='progress' raises SilentOperationInProgressException."""
        with pytest.raises(SilentOperationInProgressException):
            req(None, cancel_output="progress")

    def test_req_multiple_args_all_truthy(self) -> None:
        """Test req with multiple truthy args returns first."""
        result = req(1, 2, 3)
        assert result == 1

    def test_req_multiple_args_first_falsy(self) -> None:
        """Test req with first arg falsy raises."""
        with pytest.raises(SilentException):
            req(None, True, True)

    def test_req_multiple_args_middle_falsy(self) -> None:
        """Test req with middle arg falsy raises."""
        with pytest.raises(SilentException):
            req(True, None, True)

    def test_req_multiple_args_last_falsy(self) -> None:
        """Test req with last arg falsy raises."""
        with pytest.raises(SilentException):
            req(True, True, None)

    def test_req_no_args(self) -> None:
        """Test req with no args returns None."""
        result = req()
        assert result is None

    def test_req_dict_truthy(self) -> None:
        """Test req with non-empty dict passes."""
        result = req({"key": "value"})
        assert result == {"key": "value"}

    def test_req_dict_empty_raises(self) -> None:
        """Test req with empty dict raises."""
        with pytest.raises(SilentException):
            req({})
