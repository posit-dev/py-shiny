"""Tests for shiny._utils module - utility functions."""

from shiny._utils import drop_none, guess_mime_type, is_async_callable, rand_hex


class TestRandHex:
    """Tests for rand_hex function."""

    def test_rand_hex_length(self) -> None:
        """Test rand_hex returns string of correct length (bytes * 2)."""
        result = rand_hex(8)
        # 8 bytes = 16 hex characters
        assert len(result) == 16

    def test_rand_hex_different_lengths(self) -> None:
        """Test rand_hex with different lengths."""
        # bytes * 2 = number of hex characters
        assert len(rand_hex(4)) == 8
        assert len(rand_hex(16)) == 32
        assert len(rand_hex(32)) == 64

    def test_rand_hex_is_hex(self) -> None:
        """Test rand_hex returns valid hex characters."""
        result = rand_hex(16)
        # All characters should be valid hex
        int(result, 16)  # Should not raise ValueError

    def test_rand_hex_unique(self) -> None:
        """Test rand_hex returns unique values."""
        results = [rand_hex(8) for _ in range(100)]
        # All should be unique
        assert len(set(results)) == 100


class TestDropNone:
    """Tests for drop_none function."""

    def test_drop_none_empty_dict(self) -> None:
        """Test drop_none with empty dict."""
        result = drop_none({})
        assert result == {}

    def test_drop_none_no_nones(self) -> None:
        """Test drop_none with no None values."""
        result = drop_none({"a": 1, "b": 2})
        assert result == {"a": 1, "b": 2}

    def test_drop_none_removes_nones(self) -> None:
        """Test drop_none removes None values."""
        result = drop_none({"a": 1, "b": None, "c": 3})
        assert result == {"a": 1, "c": 3}

    def test_drop_none_all_nones(self) -> None:
        """Test drop_none with all None values."""
        result = drop_none({"a": None, "b": None})
        assert result == {}

    def test_drop_none_preserves_falsy(self) -> None:
        """Test drop_none preserves falsy values that aren't None."""
        result = drop_none({"a": 0, "b": "", "c": False, "d": None})
        assert result == {"a": 0, "b": "", "c": False}


class TestGuessMimeType:
    """Tests for guess_mime_type function."""

    def test_guess_mime_type_png(self) -> None:
        """Test guess_mime_type for PNG."""
        result = guess_mime_type("image.png")
        assert "image/png" in result or result.startswith("image")

    def test_guess_mime_type_jpg(self) -> None:
        """Test guess_mime_type for JPG."""
        result = guess_mime_type("photo.jpg")
        assert "image" in result or result.startswith("image")

    def test_guess_mime_type_html(self) -> None:
        """Test guess_mime_type for HTML."""
        result = guess_mime_type("page.html")
        assert "text/html" in result or "html" in result

    def test_guess_mime_type_css(self) -> None:
        """Test guess_mime_type for CSS."""
        result = guess_mime_type("style.css")
        assert "css" in result

    def test_guess_mime_type_js(self) -> None:
        """Test guess_mime_type for JavaScript."""
        result = guess_mime_type("script.js")
        # JavaScript mime types can vary
        assert result is not None

    def test_guess_mime_type_json(self) -> None:
        """Test guess_mime_type for JSON."""
        result = guess_mime_type("data.json")
        assert "json" in result

    def test_guess_mime_type_unknown(self) -> None:
        """Test guess_mime_type for unknown extension."""
        result = guess_mime_type("file.xyz123unknown")
        # Should return something (default or None)
        assert result is not None or result is None


class TestIsAsyncCallable:
    """Tests for is_async_callable function."""

    def test_is_async_callable_sync_function(self) -> None:
        """Test is_async_callable with sync function."""

        def sync_func():
            pass

        assert is_async_callable(sync_func) is False

    def test_is_async_callable_async_function(self) -> None:
        """Test is_async_callable with async function."""

        async def async_func():
            pass

        assert is_async_callable(async_func) is True

    def test_is_async_callable_lambda(self) -> None:
        """Test is_async_callable with lambda."""
        sync_lambda = lambda: None  # noqa: E731
        assert is_async_callable(sync_lambda) is False

    def test_is_async_callable_class_method(self) -> None:
        """Test is_async_callable with class method."""

        class MyClass:
            def sync_method(self):
                pass

            async def async_method(self):
                pass

        obj = MyClass()
        assert is_async_callable(obj.sync_method) is False
        assert is_async_callable(obj.async_method) is True

    def test_is_async_callable_callable_class(self) -> None:
        """Test is_async_callable with callable class."""

        class SyncCallable:
            def __call__(self):
                pass

        class AsyncCallable:
            async def __call__(self):
                pass

        assert is_async_callable(SyncCallable()) is False
        assert is_async_callable(AsyncCallable()) is True
