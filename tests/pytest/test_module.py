"""Tests for shiny.module module."""

from shiny.module import ui, server, current_namespace, resolve_id, ResolvedId
from shiny._namespaces import namespace_context


class TestModuleUI:
    """Tests for the module.ui decorator."""

    def test_ui_decorator_wraps_function(self):
        """Test that ui decorator wraps a function correctly."""

        @ui
        def my_ui():
            return "test"

        # The wrapped function should accept an id parameter
        result = my_ui("my_id")
        assert result == "test"

    def test_ui_decorator_with_args(self):
        """Test ui decorator with function that has arguments."""

        @ui
        def my_ui(label: str, value: int = 10):
            return f"{label}: {value}"

        result = my_ui("my_id", "Label", value=20)
        assert result == "Label: 20"

    def test_ui_namespace_context(self):
        """Test that ui decorator sets up namespace context."""

        @ui
        def my_ui():
            return current_namespace()

        ns = my_ui("test_ns")
        assert ns == "test_ns"


class TestModuleServer:
    """Tests for the module.server decorator."""

    def test_server_decorator_signature(self):
        """Test that server decorator exists and is callable."""

        @server
        def my_server(input, output, session, value: int = 10):
            return value

        # Server decorator should work (actual execution requires session)
        assert callable(my_server)


class TestResolveId:
    """Tests for the resolve_id function."""

    def test_resolve_id_no_namespace(self):
        """Test resolve_id with no active namespace."""
        result = resolve_id("my_input")
        assert result == "my_input"

    def test_resolve_id_with_namespace(self):
        """Test resolve_id within a namespace context."""
        with namespace_context("my_ns"):
            result = resolve_id("my_input")
            assert result == "my_ns-my_input"

    def test_resolve_id_nested_namespaces(self):
        """Test resolve_id with nested namespaces."""
        with namespace_context("outer"):
            with namespace_context("inner"):
                result = resolve_id("my_input")
                assert result == "outer-inner-my_input"


class TestCurrentNamespace:
    """Tests for the current_namespace function."""

    def test_current_namespace_none(self):
        """Test current_namespace with no active namespace."""
        ns = current_namespace()
        assert ns == ""

    def test_current_namespace_with_context(self):
        """Test current_namespace within a context."""
        with namespace_context("test_ns"):
            ns = current_namespace()
            assert ns == "test_ns"

    def test_current_namespace_nested(self):
        """Test current_namespace with nested contexts."""
        with namespace_context("outer"):
            assert current_namespace() == "outer"
            with namespace_context("inner"):
                assert current_namespace() == "outer-inner"
            assert current_namespace() == "outer"


class TestResolvedId:
    """Tests for ResolvedId class."""

    def test_resolved_id_creation(self):
        """Test creating a ResolvedId."""
        rid = ResolvedId("my_id")
        assert str(rid) == "my_id"

    def test_resolved_id_from_resolved(self):
        """Test creating ResolvedId from another ResolvedId."""
        rid1 = ResolvedId("first")
        rid2 = ResolvedId(rid1)
        assert str(rid2) == "first"

    def test_resolved_id_call(self):
        """Test calling ResolvedId to create child id."""
        rid = ResolvedId("parent")
        child = rid("child")
        assert str(child) == "parent-child"

    def test_resolved_id_equality(self):
        """Test ResolvedId equality."""
        rid1 = ResolvedId("test")
        rid2 = ResolvedId("test")
        assert rid1 == rid2

    def test_resolved_id_hash(self):
        """Test ResolvedId is hashable."""
        rid = ResolvedId("test")
        d = {rid: "value"}
        assert d[ResolvedId("test")] == "value"
