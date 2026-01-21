"""Tests for shiny/_utils.py - Utility functions"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

import pytest

from shiny._utils import (
    CancelledError,
    drop_none,
    guess_mime_type,
    is_async_callable,
    lists_to_tuples,
    private_random_id,
    private_random_int,
    rand_hex,
    run_coro_sync,
    sort_keys_length,
    wrap_async,
)


class TestRandHex:
    """Tests for the rand_hex function."""

    def test_basic_rand_hex(self) -> None:
        """Test generating random hex string."""
        result = rand_hex(4)
        assert len(result) == 8  # 4 bytes = 8 hex characters
        assert all(c in "0123456789abcdef" for c in result)

    def test_rand_hex_different_values(self) -> None:
        """Test that rand_hex generates different values."""
        results = [rand_hex(4) for _ in range(10)]
        # All should be unique (probability of collision is extremely low)
        assert len(set(results)) == 10

    def test_rand_hex_various_sizes(self) -> None:
        """Test rand_hex with various sizes."""
        for size in [1, 2, 4, 8, 16]:
            result = rand_hex(size)
            assert len(result) == size * 2


class TestDropNone:
    """Tests for the drop_none function."""

    def test_drops_none_values(self) -> None:
        """Test that None values are dropped."""
        result = drop_none({"a": 1, "b": None, "c": 3})
        assert result == {"a": 1, "c": 3}

    def test_empty_dict(self) -> None:
        """Test with empty dict."""
        result = drop_none({})
        assert result == {}

    def test_all_none(self) -> None:
        """Test with all None values."""
        result = drop_none({"a": None, "b": None})
        assert result == {}

    def test_no_none(self) -> None:
        """Test with no None values."""
        result = drop_none({"a": 1, "b": 2})
        assert result == {"a": 1, "b": 2}

    def test_preserves_falsy_values(self) -> None:
        """Test that falsy values other than None are preserved."""
        result = drop_none({"a": 0, "b": False, "c": "", "d": None})
        assert result == {"a": 0, "b": False, "c": ""}


class TestListsToTuples:
    """Tests for the lists_to_tuples function."""

    def test_simple_list(self) -> None:
        """Test converting simple list to tuple."""
        result = lists_to_tuples([1, 2, 3])
        assert result == (1, 2, 3)

    def test_nested_list(self) -> None:
        """Test converting nested lists."""
        result = lists_to_tuples([[1, 2], [3, 4]])
        assert result == ((1, 2), (3, 4))

    def test_dict_with_lists(self) -> None:
        """Test converting dict containing lists."""
        result = lists_to_tuples({"a": [1, 2], "b": [3, 4]})
        assert result == {"a": (1, 2), "b": (3, 4)}

    def test_non_list_unchanged(self) -> None:
        """Test that non-list values are unchanged."""
        result = lists_to_tuples("hello")
        assert result == "hello"

        result = lists_to_tuples(42)
        assert result == 42

    def test_deeply_nested(self) -> None:
        """Test deeply nested structure."""
        result = lists_to_tuples({"a": {"b": [1, [2, 3]]}})
        assert result == {"a": {"b": (1, (2, 3))}}


class TestSortKeysLength:
    """Tests for the sort_keys_length function."""

    def test_ascending_sort(self) -> None:
        """Test sorting keys by length ascending."""
        result = sort_keys_length({"abc": 1, "a": 2, "ab": 3})
        assert list(result.keys()) == ["a", "ab", "abc"]

    def test_descending_sort(self) -> None:
        """Test sorting keys by length descending."""
        result = sort_keys_length({"abc": 1, "a": 2, "ab": 3}, descending=True)
        assert list(result.keys()) == ["abc", "ab", "a"]

    def test_empty_dict(self) -> None:
        """Test sorting empty dict."""
        result = sort_keys_length({})
        assert result == {}

    def test_preserves_values(self) -> None:
        """Test that values are preserved."""
        original = {"abc": 1, "a": 2, "ab": 3}
        result = sort_keys_length(original)
        assert result["abc"] == 1
        assert result["a"] == 2
        assert result["ab"] == 3


class TestGuessMimeType:
    """Tests for the guess_mime_type function."""

    def test_javascript_file(self) -> None:
        """Test guessing MIME type for JavaScript file."""
        assert guess_mime_type("script.js") == "text/javascript"
        assert guess_mime_type("module.mjs") == "text/javascript"
        assert guess_mime_type("common.cjs") == "text/javascript"

    def test_html_file(self) -> None:
        """Test guessing MIME type for HTML file."""
        result = guess_mime_type("page.html")
        assert result == "text/html"

    def test_css_file(self) -> None:
        """Test guessing MIME type for CSS file."""
        result = guess_mime_type("style.css")
        assert result == "text/css"

    def test_unknown_extension(self) -> None:
        """Test default for unknown extension."""
        result = guess_mime_type("file.qwerty123")
        assert result == "application/octet-stream"

    def test_custom_default(self) -> None:
        """Test custom default MIME type."""
        result = guess_mime_type("file.qwerty123", default="application/custom")
        assert result == "application/custom"

    def test_path_object(self) -> None:
        """Test with Path object."""
        result = guess_mime_type(Path("script.js"))
        assert result == "text/javascript"


class TestPrivateRandomId:
    """Tests for the private_random_id function."""

    def test_basic_id(self) -> None:
        """Test generating basic random ID."""
        result = private_random_id()
        assert len(result) == 6  # 3 bytes = 6 hex chars

    def test_id_with_prefix(self) -> None:
        """Test generating ID with prefix."""
        result = private_random_id("test")
        assert result.startswith("test_")
        assert len(result) == 11  # "test_" + 6 hex chars

    def test_prefix_no_underscore(self) -> None:
        """Test that underscore is added if missing."""
        result = private_random_id("prefix")
        assert result.startswith("prefix_")

    def test_prefix_with_underscore(self) -> None:
        """Test that double underscore is not added."""
        result = private_random_id("prefix_")
        assert result.startswith("prefix_")
        assert not result.startswith("prefix__")

    def test_custom_bytes(self) -> None:
        """Test ID with custom byte size."""
        result = private_random_id("", bytes=8)
        assert len(result) == 16  # 8 bytes = 16 hex chars


class TestPrivateRandomInt:
    """Tests for the private_random_int function."""

    def test_basic_random_int(self) -> None:
        """Test generating random int."""
        result = private_random_int(1, 100)
        assert isinstance(result, str)
        value = int(result)
        assert 1 <= value <= 100

    def test_same_range(self) -> None:
        """Test with min equals max."""
        result = private_random_int(42, 42)
        assert result == "42"


class TestIsAsyncCallable:
    """Tests for the is_async_callable function."""

    def test_regular_function(self) -> None:
        """Test with regular function."""

        def sync_func() -> int:
            return 42

        assert is_async_callable(sync_func) is False

    def test_async_function(self) -> None:
        """Test with async function."""

        async def async_func() -> int:
            return 42

        assert is_async_callable(async_func) is True

    def test_lambda(self) -> None:
        """Test with lambda."""
        assert is_async_callable(lambda: 42) is False

    def test_class_with_call(self) -> None:
        """Test with class having __call__."""

        class Callable:
            def __call__(self) -> int:
                return 42

        assert is_async_callable(Callable()) is False

    def test_class_with_async_call(self) -> None:
        """Test with class having async __call__."""

        class AsyncCallable:
            async def __call__(self) -> int:
                return 42

        assert is_async_callable(AsyncCallable()) is True


class TestWrapAsync:
    """Tests for the wrap_async function."""

    @pytest.mark.asyncio
    async def test_wrap_sync_function(self) -> None:
        """Test wrapping synchronous function."""

        def sync_func(x: int) -> int:
            return x * 2

        async_func = wrap_async(sync_func)
        result = await async_func(21)
        assert result == 42

    @pytest.mark.asyncio
    async def test_wrap_already_async(self) -> None:
        """Test wrapping already async function returns it unchanged."""

        async def async_func(x: int) -> int:
            return x * 2

        wrapped = wrap_async(async_func)
        assert wrapped is async_func  # Should be same object
        result = await wrapped(21)
        assert result == 42

    @pytest.mark.asyncio
    async def test_preserves_return_value(self) -> None:
        """Test that wrapped function preserves return value."""

        def returns_dict() -> dict[str, int]:
            return {"a": 1, "b": 2}

        wrapped = wrap_async(returns_dict)
        result = await wrapped()
        assert result == {"a": 1, "b": 2}


class TestRunCoroSync:
    """Tests for the run_coro_sync function."""

    def test_sync_coroutine(self) -> None:
        """Test running a coroutine that completes immediately."""

        async def immediate() -> int:
            return 42

        result = run_coro_sync(immediate())
        assert result == 42

    def test_non_coroutine_raises(self) -> None:
        """Test that non-coroutine raises TypeError."""
        with pytest.raises(TypeError, match="requires a Coroutine"):
            run_coro_sync("not a coroutine")  # type: ignore

    def test_yielding_coroutine_raises(self) -> None:
        """Test that yielding coroutine raises RuntimeError."""

        async def yielding() -> int:
            await asyncio.sleep(0)  # This yields control
            return 42

        with pytest.raises(RuntimeError, match="yielded control"):
            run_coro_sync(yielding())


class TestCancelledError:
    """Test CancelledError is correctly exported."""

    def test_cancelled_error_is_asyncio(self) -> None:
        """Test CancelledError is asyncio's CancelledError."""
        assert CancelledError is asyncio.CancelledError
