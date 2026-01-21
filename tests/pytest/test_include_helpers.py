"""Tests for shiny/ui/_include_helpers.py - Include helpers for JS/CSS."""

import os
import tempfile
from pathlib import Path

import pytest

from shiny.ui._include_helpers import (
    check_path,
    get_file_key,
    get_hash,
    hash_deterministic,
    include_css,
    include_js,
    read_utf8,
)


class TestIncludeJs:
    """Tests for include_js function."""

    def test_include_js_inline(self):
        """Test include_js with inline method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            js_file = os.path.join(tmpdir, "test.js")
            with open(js_file, "w") as f:
                f.write('console.log("hello");')

            tag = include_js(js_file, method="inline")
            html = str(tag)
            assert "<script>" in html
            assert 'console.log("hello")' in html

    def test_include_js_link(self):
        """Test include_js with link method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            js_file = os.path.join(tmpdir, "test.js")
            with open(js_file, "w") as f:
                f.write('console.log("hello");')

            tag = include_js(js_file, method="link")
            html = str(tag)
            assert "<script" in html
            assert "src=" in html

    def test_include_js_with_kwargs(self):
        """Test include_js passes additional kwargs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            js_file = os.path.join(tmpdir, "test.js")
            with open(js_file, "w") as f:
                f.write('console.log("hello");')

            tag = include_js(js_file, method="inline", id="my-script")
            html = str(tag)
            assert 'id="my-script"' in html


class TestIncludeCss:
    """Tests for include_css function."""

    def test_include_css_inline(self):
        """Test include_css with inline method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            css_file = os.path.join(tmpdir, "test.css")
            with open(css_file, "w") as f:
                f.write("body { color: red; }")

            tag = include_css(css_file, method="inline")
            html = str(tag)
            assert "<style" in html
            assert "body { color: red; }" in html

    def test_include_css_link(self):
        """Test include_css with link method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            css_file = os.path.join(tmpdir, "test.css")
            with open(css_file, "w") as f:
                f.write("body { color: red; }")

            tag = include_css(css_file, method="link")
            html = str(tag)
            assert "<link" in html
            assert "href=" in html
            assert 'rel="stylesheet"' in html


class TestCheckPath:
    """Tests for check_path function."""

    def test_check_path_existing_file(self):
        """Test check_path with existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            try:
                result = check_path(f.name)
                assert isinstance(result, Path)
                assert result.exists()
            finally:
                os.unlink(f.name)

    def test_check_path_nonexistent_raises(self):
        """Test check_path raises for nonexistent file."""
        with pytest.raises(RuntimeError, match="does not exist"):
            check_path("/nonexistent/file.txt")

    def test_check_path_string(self):
        """Test check_path accepts string path."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            try:
                result = check_path(f.name)
                assert isinstance(result, Path)
            finally:
                os.unlink(f.name)

    def test_check_path_pathlib(self):
        """Test check_path accepts Path object."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            try:
                result = check_path(Path(f.name))
                assert isinstance(result, Path)
            finally:
                os.unlink(f.name)


class TestReadUtf8:
    """Tests for read_utf8 function."""

    def test_read_utf8_basic(self):
        """Test reading basic UTF-8 content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Hello, World!")

            content = read_utf8(file_path)
            assert content == "Hello, World!"

    def test_read_utf8_unicode(self):
        """Test reading UTF-8 content with unicode characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Hello, 世界! 🌍")

            content = read_utf8(file_path)
            assert content == "Hello, 世界! 🌍"

    def test_read_utf8_multiline(self):
        """Test reading multiline content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("line1\nline2\nline3")

            content = read_utf8(file_path)
            assert "line1" in content
            assert "line2" in content
            assert "line3" in content


class TestHashDeterministic:
    """Tests for hash_deterministic function."""

    def test_hash_deterministic_same_input(self):
        """Test same input produces same hash."""
        hash1 = hash_deterministic("test input")
        hash2 = hash_deterministic("test input")
        assert hash1 == hash2

    def test_hash_deterministic_different_input(self):
        """Test different inputs produce different hashes."""
        hash1 = hash_deterministic("input1")
        hash2 = hash_deterministic("input2")
        assert hash1 != hash2

    def test_hash_deterministic_returns_string(self):
        """Test hash returns a string."""
        result = hash_deterministic("test")
        assert isinstance(result, str)

    def test_hash_deterministic_hex_format(self):
        """Test hash is in hex format (SHA1 = 40 chars)."""
        result = hash_deterministic("test")
        assert len(result) == 40
        assert all(c in "0123456789abcdef" for c in result)


class TestGetFileKey:
    """Tests for get_file_key function."""

    def test_get_file_key_includes_path(self):
        """Test file key includes path."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            try:
                key = get_file_key(f.name)
                assert f.name in key
            finally:
                os.unlink(f.name)

    def test_get_file_key_includes_mtime(self):
        """Test file key includes modification time."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            try:
                key = get_file_key(f.name)
                # Key should contain a dash separator
                assert "-" in key
                # The part after the dash should be a number (mtime)
                parts = key.rsplit("-", 1)
                assert len(parts) == 2
            finally:
                os.unlink(f.name)

    def test_get_file_key_string_path(self):
        """Test file key works with string path."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            try:
                key = get_file_key(f.name)
                assert isinstance(key, str)
            finally:
                os.unlink(f.name)

    def test_get_file_key_path_object(self):
        """Test file key works with Path object."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            try:
                key = get_file_key(Path(f.name))
                assert isinstance(key, str)
            finally:
                os.unlink(f.name)


class TestGetHash:
    """Tests for get_hash function."""

    def test_get_hash_single_file(self):
        """Test get_hash with single file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            try:
                f.write(b"test content")
                f.flush()
                hash_val = get_hash(f.name, include_files=False)
                assert isinstance(hash_val, str)
                assert len(hash_val) == 40
            finally:
                os.unlink(f.name)

    def test_get_hash_with_include_files(self):
        """Test get_hash with include_files=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = os.path.join(tmpdir, "test1.txt")
            file2 = os.path.join(tmpdir, "test2.txt")
            with open(file1, "w") as f:
                f.write("content1")
            with open(file2, "w") as f:
                f.write("content2")

            hash_val = get_hash(file1, include_files=True)
            assert isinstance(hash_val, str)
            assert len(hash_val) == 40

    def test_get_hash_different_for_different_files(self):
        """Test different files produce different hashes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = os.path.join(tmpdir, "test1.txt")
            file2 = os.path.join(tmpdir, "subdir", "test2.txt")
            os.makedirs(os.path.dirname(file2))
            with open(file1, "w") as f:
                f.write("content1")
            with open(file2, "w") as f:
                f.write("content2")

            hash1 = get_hash(file1, include_files=False)
            hash2 = get_hash(file2, include_files=False)
            assert hash1 != hash2
