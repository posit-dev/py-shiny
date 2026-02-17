"""Unit tests for shiny._utils module."""

from __future__ import annotations

from pathlib import Path

from shiny._utils import (
    drop_none,
    guess_mime_type,
    lists_to_tuples,
    rand_hex,
    sort_keys_length,
)


class TestRandHex:
    """Tests for rand_hex function."""

    def test_rand_hex_length(self) -> None:
        """Test rand_hex produces correct length."""
        result = rand_hex(8)
        assert len(result) == 16  # 8 bytes = 16 hex chars

    def test_rand_hex_length_4(self) -> None:
        """Test rand_hex with 4 bytes."""
        result = rand_hex(4)
        assert len(result) == 8

    def test_rand_hex_length_16(self) -> None:
        """Test rand_hex with 16 bytes."""
        result = rand_hex(16)
        assert len(result) == 32

    def test_rand_hex_is_hex(self) -> None:
        """Test rand_hex produces valid hex string."""
        result = rand_hex(8)
        # Try to convert to int using base 16
        int(result, 16)  # Should not raise

    def test_rand_hex_unique(self) -> None:
        """Test rand_hex produces unique values."""
        results = [rand_hex(8) for _ in range(100)]
        assert len(set(results)) == 100  # All should be unique


class TestDropNone:
    """Tests for drop_none function."""

    def test_drop_none_removes_none_values(self) -> None:
        """Test drop_none removes None values."""
        result = drop_none({"a": 1, "b": None, "c": 3})
        assert result == {"a": 1, "c": 3}

    def test_drop_none_empty_dict(self) -> None:
        """Test drop_none with empty dict."""
        result = drop_none({})
        assert result == {}

    def test_drop_none_all_none(self) -> None:
        """Test drop_none with all None values."""
        result = drop_none({"a": None, "b": None})
        assert result == {}

    def test_drop_none_no_none(self) -> None:
        """Test drop_none with no None values."""
        result = drop_none({"a": 1, "b": "two", "c": 3.0})
        assert result == {"a": 1, "b": "two", "c": 3.0}

    def test_drop_none_preserves_falsy_values(self) -> None:
        """Test drop_none preserves falsy values like 0, '', False."""
        result = drop_none({"a": 0, "b": "", "c": False, "d": None})
        assert result == {"a": 0, "b": "", "c": False}


class TestListsToTuples:
    """Tests for lists_to_tuples function."""

    def test_lists_to_tuples_converts_list(self) -> None:
        """Test lists_to_tuples converts lists to tuples."""
        result = lists_to_tuples([1, 2, 3])
        assert result == (1, 2, 3)
        assert isinstance(result, tuple)

    def test_lists_to_tuples_nested_list(self) -> None:
        """Test lists_to_tuples with nested lists."""
        result = lists_to_tuples([1, [2, 3], 4])
        assert result == (1, (2, 3), 4)

    def test_lists_to_tuples_dict_with_list_values(self) -> None:
        """Test lists_to_tuples with dict containing list values."""
        result = lists_to_tuples({"a": [1, 2], "b": [3, 4]})
        assert result == {"a": (1, 2), "b": (3, 4)}

    def test_lists_to_tuples_preserves_non_iterables(self) -> None:
        """Test lists_to_tuples preserves non-list values."""
        result = lists_to_tuples(42)
        assert result == 42

    def test_lists_to_tuples_string(self) -> None:
        """Test lists_to_tuples preserves strings."""
        result = lists_to_tuples("hello")
        assert result == "hello"

    def test_lists_to_tuples_empty_list(self) -> None:
        """Test lists_to_tuples with empty list."""
        result = lists_to_tuples([])
        assert result == ()

    def test_lists_to_tuples_complex_structure(self) -> None:
        """Test lists_to_tuples with complex nested structure."""
        input_data = {"a": [1, {"b": [2, 3]}], "c": [[4, 5], [6, 7]]}
        result = lists_to_tuples(input_data)
        expected = {"a": (1, {"b": (2, 3)}), "c": ((4, 5), (6, 7))}
        assert result == expected


class TestSortKeysLength:
    """Tests for sort_keys_length function."""

    def test_sort_keys_length_ascending(self) -> None:
        """Test sort_keys_length ascending order."""
        input_dict = {"medium": 2, "a": 1, "longer_key": 3}
        result = sort_keys_length(input_dict)
        keys = list(result.keys())
        assert keys == ["a", "medium", "longer_key"]

    def test_sort_keys_length_descending(self) -> None:
        """Test sort_keys_length descending order."""
        input_dict = {"medium": 2, "a": 1, "longer_key": 3}
        result = sort_keys_length(input_dict, descending=True)
        keys = list(result.keys())
        assert keys == ["longer_key", "medium", "a"]

    def test_sort_keys_length_preserves_values(self) -> None:
        """Test sort_keys_length preserves values."""
        input_dict = {"bb": 2, "a": 1, "ccc": 3}
        result = sort_keys_length(input_dict)
        assert result["a"] == 1
        assert result["bb"] == 2
        assert result["ccc"] == 3

    def test_sort_keys_length_empty_dict(self) -> None:
        """Test sort_keys_length with empty dict."""
        result: dict[str, object] = sort_keys_length({})
        assert result == {}

    def test_sort_keys_length_same_length_keys(self) -> None:
        """Test sort_keys_length with same length keys."""
        input_dict = {"ab": 1, "cd": 2, "ef": 3}
        result = sort_keys_length(input_dict)
        # All same length, order depends on Python's sort stability
        assert len(result) == 3


class TestGuessMimeType:
    """Tests for guess_mime_type function."""

    def test_guess_mime_type_html(self) -> None:
        """Test guess_mime_type for HTML file."""
        result = guess_mime_type("test.html")
        assert result == "text/html"

    def test_guess_mime_type_css(self) -> None:
        """Test guess_mime_type for CSS file."""
        result = guess_mime_type("test.css")
        assert result == "text/css"

    def test_guess_mime_type_js(self) -> None:
        """Test guess_mime_type for JavaScript file."""
        result = guess_mime_type("test.js")
        assert result == "text/javascript"

    def test_guess_mime_type_mjs(self) -> None:
        """Test guess_mime_type for ES module JavaScript file."""
        result = guess_mime_type("test.mjs")
        assert result == "text/javascript"

    def test_guess_mime_type_cjs(self) -> None:
        """Test guess_mime_type for CommonJS file."""
        result = guess_mime_type("test.cjs")
        assert result == "text/javascript"

    def test_guess_mime_type_json(self) -> None:
        """Test guess_mime_type for JSON file."""
        result = guess_mime_type("test.json")
        assert result == "application/json"

    def test_guess_mime_type_png(self) -> None:
        """Test guess_mime_type for PNG file."""
        result = guess_mime_type("test.png")
        assert result == "image/png"

    def test_guess_mime_type_jpg(self) -> None:
        """Test guess_mime_type for JPEG file."""
        result = guess_mime_type("test.jpg")
        assert result == "image/jpeg"

    def test_guess_mime_type_unknown(self) -> None:
        """Test guess_mime_type for unknown file type."""
        result = guess_mime_type("test.xyz123unknown")
        assert result == "application/octet-stream"

    def test_guess_mime_type_custom_default(self) -> None:
        """Test guess_mime_type with custom default."""
        result = guess_mime_type("test.xyz123unknown", default="custom/type")
        assert result == "custom/type"

    def test_guess_mime_type_path_object(self) -> None:
        """Test guess_mime_type with Path object."""
        result = guess_mime_type(Path("test.html"))
        assert result == "text/html"

    def test_guess_mime_type_empty_string(self) -> None:
        """Test guess_mime_type with empty string."""
        result = guess_mime_type("")
        assert result == "application/octet-stream"

    def test_guess_mime_type_svg(self) -> None:
        """Test guess_mime_type for SVG file."""
        result = guess_mime_type("test.svg")
        # SVG should be image/svg+xml
        assert "svg" in result
