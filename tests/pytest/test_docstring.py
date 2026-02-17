"""Tests for shiny/_docstring.py - Docstring utilities and example handling."""

import os
import tempfile
from unittest.mock import patch

import pytest

from shiny._docstring import (
    DocStringWithExample,
    ExampleNotFoundException,
    ExampleWriter,
    ExpressExampleNotFoundException,
    app_choose_core_or_express,
    doc_format,
    find_api_examples_dir,
    get_decorated_source_directory,
    is_express_app,
    no_example,
)


class TestFindApiExamplesDir:
    """Tests for find_api_examples_dir function."""

    def test_find_api_examples_dir_exists(self):
        """Test finding api-examples directory when it exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create api-examples directory
            api_examples_dir = os.path.join(tmpdir, "api-examples")
            os.makedirs(api_examples_dir)

            result = find_api_examples_dir(tmpdir)
            assert result == api_examples_dir

    def test_find_api_examples_dir_in_parent(self):
        """Test finding api-examples directory in parent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create api-examples in root
            api_examples_dir = os.path.join(tmpdir, "api-examples")
            os.makedirs(api_examples_dir)

            # Create a subdirectory
            subdir = os.path.join(tmpdir, "subdir")
            os.makedirs(subdir)

            result = find_api_examples_dir(subdir)
            assert result == api_examples_dir

    def test_find_api_examples_dir_not_found(self):
        """Test returns None when no api-examples directory exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create pyproject.toml to mark as root
            with open(os.path.join(tmpdir, "pyproject.toml"), "w") as f:
                f.write("")

            subdir = os.path.join(tmpdir, "subdir")
            os.makedirs(subdir)

            result = find_api_examples_dir(subdir)
            assert result is None

    def test_find_api_examples_dir_stops_at_root_files(self):
        """Test stops searching at package root markers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create setup.cfg to mark root
            with open(os.path.join(tmpdir, "setup.cfg"), "w") as f:
                f.write("")

            result = find_api_examples_dir(tmpdir)
            assert result is None


class TestDocStringWithExample:
    """Tests for DocStringWithExample class."""

    def test_docstring_with_example_is_string(self):
        """Test that DocStringWithExample is a string subclass."""
        doc = DocStringWithExample("This is a docstring")
        assert isinstance(doc, str)
        assert doc == "This is a docstring"

    def test_docstring_with_example_preserves_content(self):
        """Test that content is preserved."""
        content = "Test docstring\n\nWith multiple lines."
        doc = DocStringWithExample(content)
        assert str(doc) == content


class TestExampleWriter:
    """Tests for ExampleWriter class."""

    def test_write_example_reads_file(self):
        """Test that write_example reads file content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_file = os.path.join(tmpdir, "app.py")
            with open(app_file, "w") as f:
                f.write("from shiny import App\napp = App()")

            writer = ExampleWriter()
            result = writer.write_example([app_file])

            assert "from shiny import App" in result
            assert "app = App()" in result
            assert "```.python" in result


class TestNoExample:
    """Tests for no_example decorator."""

    _no_example_attr_name = "__no_example"

    def test_no_example_sets_attribute(self):
        """Test that no_example sets __no_example attribute."""

        @no_example()
        def my_func():
            pass

        assert hasattr(my_func, self._no_example_attr_name)
        no_example_attr = getattr(my_func, self._no_example_attr_name)
        assert "express" in no_example_attr
        assert "core" in no_example_attr

    def test_no_example_express_only(self):
        """Test no_example with express mode only."""

        @no_example(mode="express")
        def my_func():
            pass

        assert hasattr(my_func, self._no_example_attr_name)
        no_example_attr = getattr(my_func, self._no_example_attr_name)
        assert "express" in no_example_attr
        assert "core" not in no_example_attr

    def test_no_example_core_only(self):
        """Test no_example with core mode only."""

        @no_example(mode="core")
        def my_func():
            pass

        assert hasattr(my_func, self._no_example_attr_name)
        no_example_attr = getattr(my_func, self._no_example_attr_name)
        assert "core" in no_example_attr
        assert "express" not in no_example_attr

    def test_no_example_multiple_applications(self):
        """Test applying no_example multiple times."""

        @no_example(mode="core")
        @no_example(mode="express")
        def my_func():
            pass

        no_example_attr = getattr(my_func, self._no_example_attr_name)
        assert "express" in no_example_attr
        assert "core" in no_example_attr


class TestIsExpressApp:
    """Tests for is_express_app function."""

    def test_is_express_app_with_from_import(self):
        """Test detection of 'from shiny.express' import."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_file = os.path.join(tmpdir, "app.py")
            with open(app_file, "w") as f:
                f.write("from shiny.express import input, output")

            assert is_express_app(app_file) is True

    def test_is_express_app_with_import_statement(self):
        """Test detection of 'import shiny.express' statement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_file = os.path.join(tmpdir, "app.py")
            with open(app_file, "w") as f:
                f.write("import shiny.express")

            assert is_express_app(app_file) is True

    def test_is_express_app_core_app(self):
        """Test that core app is not detected as express."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_file = os.path.join(tmpdir, "app.py")
            with open(app_file, "w") as f:
                f.write("from shiny import App, ui")

            assert is_express_app(app_file) is False

    def test_is_express_app_nonexistent(self):
        """Test that nonexistent file returns False."""
        assert is_express_app("/nonexistent/path/app.py") is False


class TestExampleNotFoundException:
    """Tests for ExampleNotFoundException class."""

    def test_exception_message_single_file(self):
        """Test exception message with single file name."""
        exc = ExampleNotFoundException("app.py", "/some/dir", "core")
        msg = str(exc)
        assert "app.py" in msg
        assert "/some/dir" in msg
        assert "Core" in msg

    def test_exception_message_multiple_files(self):
        """Test exception message with multiple file names."""
        exc = ExampleNotFoundException(["app.py", "app-core.py"], "/some/dir", "core")
        msg = str(exc)
        assert "app.py" in msg
        assert "app-core.py" in msg
        assert " or " in msg

    def test_exception_message_express_type(self):
        """Test exception message with express type."""
        exc = ExampleNotFoundException("app.py", "/some/dir", "express")
        msg = str(exc)
        assert "Express" in msg


class TestExpressExampleNotFoundException:
    """Tests for ExpressExampleNotFoundException class."""

    def test_is_example_not_found_subclass(self):
        """Test that it's a subclass of ExampleNotFoundException."""
        exc = ExpressExampleNotFoundException("app.py", "/dir")
        assert isinstance(exc, ExampleNotFoundException)

    def test_type_is_express(self):
        """Test that type is always express."""
        exc = ExpressExampleNotFoundException("app.py", "/dir")
        assert exc.type == "express"


class TestAppChooseCoreOrExpress:
    """Tests for app_choose_core_or_express function."""

    def test_returns_existing_express_app(self):
        """Test returns express app when it exists and is express."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_file = os.path.join(tmpdir, "app.py")
            with open(app_file, "w") as f:
                f.write("from shiny.express import input")

            with patch.dict(os.environ, {"SHINY_MODE": "express"}):
                result = app_choose_core_or_express(app_file, mode="express")
                assert result == app_file

    def test_returns_express_variant(self):
        """Test returns app-express.py when main file is not express."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create core app.py
            app_file = os.path.join(tmpdir, "app.py")
            with open(app_file, "w") as f:
                f.write("from shiny import App")

            # Create express variant
            express_file = os.path.join(tmpdir, "app-express.py")
            with open(express_file, "w") as f:
                f.write("from shiny.express import input")

            result = app_choose_core_or_express(app_file, mode="express")
            assert result == express_file

    def test_returns_core_app(self):
        """Test returns core app when mode is core."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_file = os.path.join(tmpdir, "app.py")
            with open(app_file, "w") as f:
                f.write("from shiny import App")

            result = app_choose_core_or_express(app_file, mode="core")
            assert result == app_file

    def test_falls_back_to_app_core(self):
        """Test falls back to app-core.py when app.py doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Only create app-core.py
            core_file = os.path.join(tmpdir, "app-core.py")
            with open(core_file, "w") as f:
                f.write("from shiny import App")

            app_file = os.path.join(tmpdir, "app.py")
            result = app_choose_core_or_express(app_file, mode="core")
            assert result == core_file

    def test_raises_when_file_not_found(self):
        """Test raises ExampleNotFoundException when file not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_file = os.path.join(tmpdir, "app.py")
            with pytest.raises(ExampleNotFoundException):
                app_choose_core_or_express(app_file, mode="core")

    def test_raises_express_not_found(self):
        """Test raises ExpressExampleNotFoundException for missing express."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create core app only
            app_file = os.path.join(tmpdir, "app.py")
            with open(app_file, "w") as f:
                f.write("from shiny import App")

            with pytest.raises(ExpressExampleNotFoundException):
                app_choose_core_or_express(app_file, mode="express")


class TestDocFormat:
    """Tests for doc_format decorator."""

    def test_doc_format_substitutes_values(self):
        """Test that doc_format substitutes placeholders."""

        @doc_format(name="TestFunc", param="value")
        def my_func():
            """Function {name} with {param}."""
            pass

        assert my_func.__doc__ is not None
        assert "TestFunc" in my_func.__doc__
        assert "value" in my_func.__doc__
        assert "{name}" not in my_func.__doc__

    def test_doc_format_no_docstring(self):
        """Test doc_format with no docstring."""

        @doc_format(name="Test")
        def my_func():
            pass

        assert my_func.__doc__ is None

    def test_doc_format_after_add_example_raises(self):
        """Test that doc_format after DocStringWithExample raises."""

        def my_func():
            pass

        my_func.__doc__ = DocStringWithExample("Test {value}")

        with pytest.raises(ValueError, match="must be applied before @add_example"):
            doc_format(value="test")(my_func)


class TestGetDecoratedSourceDirectory:
    """Tests for get_decorated_source_directory function."""

    def test_returns_directory_for_function(self):
        """Test returns directory containing the function definition."""

        def local_func():
            pass

        result = get_decorated_source_directory(local_func)
        assert os.path.isdir(result)
        # Should be in the shiny directory since we import from shiny
        # (The function has __module__ pointing to this test file)
