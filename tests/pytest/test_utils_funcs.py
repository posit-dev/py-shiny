"""Tests for shiny._utils module utility functions."""

from shiny._utils import (
    drop_none,
    guess_mime_type,
    lists_to_tuples,
    private_random_id,
    private_random_int,
    rand_hex,
    random_port,
    sort_keys_length,
)


class TestRandHex:
    """Tests for rand_hex function."""

    def test_rand_hex_length(self):
        """Test that rand_hex produces correct length."""
        result = rand_hex(4)
        assert len(result) == 8

        result = rand_hex(8)
        assert len(result) == 16

    def test_rand_hex_format(self):
        """Test that rand_hex produces valid hex string."""
        result = rand_hex(4)
        # Should be valid hex
        int(result, 16)

    def test_rand_hex_unique(self):
        """Test that rand_hex produces unique values."""
        results = [rand_hex(4) for _ in range(100)]
        # Should all be unique
        assert len(set(results)) == 100


class TestDropNone:
    """Tests for drop_none function."""

    def test_drop_none_removes_none(self):
        """Test that None values are removed."""
        result = drop_none({"a": 1, "b": None, "c": 3})
        assert result == {"a": 1, "c": 3}

    def test_drop_none_empty_dict(self):
        """Test with empty dict."""
        result = drop_none({})
        assert result == {}

    def test_drop_none_no_nones(self):
        """Test dict with no None values."""
        result = drop_none({"a": 1, "b": 2})
        assert result == {"a": 1, "b": 2}

    def test_drop_none_all_nones(self):
        """Test dict with all None values."""
        result = drop_none({"a": None, "b": None})
        assert result == {}

    def test_drop_none_preserves_falsy(self):
        """Test that falsy non-None values are preserved."""
        result = drop_none({"a": 0, "b": "", "c": False, "d": [], "e": None})
        assert result == {"a": 0, "b": "", "c": False, "d": []}


class TestListsToTuples:
    """Tests for lists_to_tuples function."""

    def test_simple_list(self):
        """Test converting simple list to tuple."""
        result = lists_to_tuples([1, 2, 3])
        assert result == (1, 2, 3)
        assert isinstance(result, tuple)

    def test_nested_list(self):
        """Test converting nested lists."""
        result = lists_to_tuples([1, [2, 3], 4])
        assert result == (1, (2, 3), 4)

    def test_dict_with_lists(self):
        """Test converting dict containing lists."""
        result = lists_to_tuples({"a": [1, 2], "b": 3})
        assert result == {"a": (1, 2), "b": 3}

    def test_non_list(self):
        """Test with non-list value."""
        result = lists_to_tuples(42)
        assert result == 42

    def test_string(self):
        """Test with string value (shouldn't be converted)."""
        result = lists_to_tuples("hello")
        assert result == "hello"


class TestSortKeysLength:
    """Tests for sort_keys_length function."""

    def test_sort_ascending(self):
        """Test sorting keys by length ascending."""
        data = {"abc": 1, "a": 2, "ab": 3}
        result = sort_keys_length(data)
        keys = list(result.keys())
        assert keys == ["a", "ab", "abc"]

    def test_sort_descending(self):
        """Test sorting keys by length descending."""
        data = {"abc": 1, "a": 2, "ab": 3}
        result = sort_keys_length(data, descending=True)
        keys = list(result.keys())
        assert keys == ["abc", "ab", "a"]

    def test_empty_dict(self):
        """Test with empty dict."""
        result: dict[str, object] = sort_keys_length({})
        assert result == {}


class TestGuessMimeType:
    """Tests for guess_mime_type function."""

    def test_javascript_file(self):
        """Test MIME type for JavaScript files."""
        assert guess_mime_type("file.js") == "text/javascript"
        assert guess_mime_type("file.mjs") == "text/javascript"
        assert guess_mime_type("file.cjs") == "text/javascript"

    def test_css_file(self):
        """Test MIME type for CSS files."""
        result = guess_mime_type("style.css")
        assert result == "text/css"

    def test_html_file(self):
        """Test MIME type for HTML files."""
        result = guess_mime_type("page.html")
        assert result == "text/html"

    def test_json_file(self):
        """Test MIME type for JSON files."""
        result = guess_mime_type("data.json")
        assert result == "application/json"

    def test_unknown_extension(self):
        """Test MIME type for unknown extension."""
        result = guess_mime_type("file.unknownext123")
        # Result may vary by system; just check it returns something
        assert result is not None

    def test_custom_default(self):
        """Test custom default MIME type for truly unknown extension."""
        result = guess_mime_type("file.unknownext123", default="text/plain")
        # If system doesn't know, should return default
        assert result is not None

    def test_with_path(self):
        """Test MIME type with full path."""
        result = guess_mime_type("/path/to/file.html")
        assert result == "text/html"


class TestRandomPort:
    """Tests for random_port function."""

    def test_random_port_in_range(self):
        """Test that random_port returns port in range."""
        port = random_port(min=10000, max=10100)
        assert 10000 <= port <= 10100

    def test_random_port_default_range(self):
        """Test random_port with default range."""
        port = random_port()
        assert 1024 <= port <= 49151


class TestPrivateRandomId:
    """Tests for private_random_id function."""

    def test_private_random_id_no_prefix(self):
        """Test private_random_id without prefix."""
        result = private_random_id()
        assert len(result) == 6  # 3 bytes = 6 hex chars

    def test_private_random_id_with_prefix(self):
        """Test private_random_id with prefix."""
        result = private_random_id(prefix="test")
        assert result.startswith("test_")

    def test_private_random_id_prefix_with_underscore(self):
        """Test private_random_id with prefix ending in underscore."""
        result = private_random_id(prefix="test_")
        assert result.startswith("test_")

    def test_private_random_id_custom_bytes(self):
        """Test private_random_id with custom bytes."""
        result = private_random_id(bytes=5)
        assert len(result) == 10  # 5 bytes = 10 hex chars


class TestPrivateRandomInt:
    """Tests for private_random_int function."""

    def test_private_random_int_in_range(self):
        """Test private_random_int returns string in range."""
        result = private_random_int(1, 100)
        value = int(result)
        assert 1 <= value <= 100

    def test_private_random_int_returns_string(self):
        """Test private_random_int returns string."""
        result = private_random_int(1, 10)
        assert isinstance(result, str)
