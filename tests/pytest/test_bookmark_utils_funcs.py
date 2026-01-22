"""Tests for shiny.bookmark._utils module"""

from shiny.bookmark._utils import (
    from_json_file,
    from_json_str,
    in_shiny_server,
    to_json_file,
    to_json_str,
)


class TestInShinyServer:
    """Test in_shiny_server function"""

    def test_not_in_shiny_server(self, monkeypatch):
        """Test in_shiny_server returns False when SHINY_PORT not set"""
        monkeypatch.delenv("SHINY_PORT", raising=False)
        assert in_shiny_server() is False

    def test_in_shiny_server_empty_port(self, monkeypatch):
        """Test in_shiny_server returns False when SHINY_PORT is empty"""
        monkeypatch.setenv("SHINY_PORT", "")
        assert in_shiny_server() is False

    def test_in_shiny_server_with_port(self, monkeypatch):
        """Test in_shiny_server returns True when SHINY_PORT is set"""
        monkeypatch.setenv("SHINY_PORT", "3838")
        assert in_shiny_server() is True


class TestJsonStr:
    """Test to_json_str and from_json_str functions"""

    def test_to_json_str_dict(self):
        """Test to_json_str with dictionary"""
        result = to_json_str({"key": "value"})
        assert isinstance(result, str)
        assert "key" in result
        assert "value" in result

    def test_to_json_str_list(self):
        """Test to_json_str with list"""
        result = to_json_str([1, 2, 3])
        assert isinstance(result, str)
        assert "[" in result

    def test_to_json_str_string(self):
        """Test to_json_str with string"""
        result = to_json_str("hello")
        assert isinstance(result, str)

    def test_to_json_str_number(self):
        """Test to_json_str with number"""
        result = to_json_str(42)
        assert result == "42"

    def test_from_json_str_dict(self):
        """Test from_json_str with dict JSON"""
        result = from_json_str('{"name": "test", "value": 123}')
        assert result == {"name": "test", "value": 123}

    def test_from_json_str_list(self):
        """Test from_json_str with list JSON"""
        result = from_json_str("[1, 2, 3]")
        assert result == [1, 2, 3]

    def test_from_json_str_string(self):
        """Test from_json_str with string JSON"""
        result = from_json_str('"hello"')
        assert result == "hello"

    def test_roundtrip_json_str(self):
        """Test roundtrip to_json_str -> from_json_str"""
        original = {"nested": {"data": [1, 2, 3]}, "flag": True}
        json_str = to_json_str(original)
        result = from_json_str(json_str)
        assert result == original


class TestJsonFile:
    """Test to_json_file and from_json_file functions"""

    def test_to_json_file_creates_file(self, tmp_path):
        """Test to_json_file creates file"""
        file_path = tmp_path / "test.json"
        to_json_file({"test": "data"}, file_path)
        assert file_path.exists()

    def test_to_json_file_writes_json(self, tmp_path):
        """Test to_json_file writes valid JSON"""
        file_path = tmp_path / "test.json"
        to_json_file({"key": "value"}, file_path)
        content = file_path.read_text()
        assert "key" in content
        assert "value" in content

    def test_from_json_file_reads_data(self, tmp_path):
        """Test from_json_file reads JSON data"""
        file_path = tmp_path / "test.json"
        file_path.write_text('{"name": "test"}')
        result = from_json_file(file_path)
        assert result == {"name": "test"}

    def test_roundtrip_json_file(self, tmp_path):
        """Test roundtrip to_json_file -> from_json_file"""
        file_path = tmp_path / "roundtrip.json"
        original = {"items": [1, 2, 3], "nested": {"a": "b"}}
        to_json_file(original, file_path)
        result = from_json_file(file_path)
        assert result == original

    def test_json_file_uses_utf8(self, tmp_path):
        """Test JSON file operations use UTF-8 encoding"""
        file_path = tmp_path / "unicode.json"
        data = {"emoji": "🎉", "accented": "café"}
        to_json_file(data, file_path)
        result = from_json_file(file_path)
        assert result == data
