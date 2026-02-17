"""Tests for shiny._namespaces module."""

import pytest

from shiny._namespaces import (
    ResolvedId,
    Root,
    current_namespace,
    namespace_context,
    resolve_id,
    resolve_id_or_none,
    validate_id,
)


class TestResolvedId:
    """Tests for ResolvedId class."""

    def test_resolved_id_creation(self) -> None:
        """Test basic ResolvedId creation."""
        rid = ResolvedId("test")
        assert str(rid) == "test"

    def test_resolved_id_empty(self) -> None:
        """Test empty ResolvedId."""
        rid = ResolvedId("")
        assert str(rid) == ""

    def test_resolved_id_call_simple(self) -> None:
        """Test calling ResolvedId with simple id."""
        rid = ResolvedId("ns")
        result = rid("child")
        assert str(result) == "ns-child"

    def test_resolved_id_call_empty_root(self) -> None:
        """Test calling empty ResolvedId (root)."""
        rid = ResolvedId("")
        result = rid("child")
        assert str(result) == "child"

    def test_resolved_id_call_chained(self) -> None:
        """Test chained namespace calls."""
        rid = ResolvedId("ns1")
        result1 = rid("ns2")
        result2 = result1("child")
        assert str(result2) == "ns1-ns2-child"

    def test_resolved_id_call_with_resolved_id(self) -> None:
        """Test calling ResolvedId with another ResolvedId returns same."""
        rid = ResolvedId("ns")
        child = ResolvedId("already-resolved")
        result = rid(child)
        assert result is child

    def test_resolved_id_separator(self) -> None:
        """Test that separator is dash."""
        rid = ResolvedId("parent")
        result = rid("child")
        assert "-" in str(result)


class TestRoot:
    """Tests for Root constant."""

    def test_root_is_resolved_id(self) -> None:
        """Test that Root is a ResolvedId."""
        assert isinstance(Root, ResolvedId)

    def test_root_is_empty(self) -> None:
        """Test that Root is empty string."""
        assert str(Root) == ""


class TestValidateId:
    """Tests for validate_id function."""

    def test_valid_simple_id(self) -> None:
        """Test validation of simple id."""
        validate_id("myId")  # Should not raise

    def test_valid_underscore_id(self) -> None:
        """Test validation of id with underscore."""
        validate_id("my_id")  # Should not raise

    def test_valid_numeric_id(self) -> None:
        """Test validation of id with numbers."""
        validate_id("id123")  # Should not raise

    def test_valid_leading_dot(self) -> None:
        """Test validation of id with leading dot."""
        validate_id(".hidden")  # Should not raise

    def test_invalid_empty_string(self) -> None:
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="non-empty"):
            validate_id("")

    def test_invalid_contains_dash(self) -> None:
        """Test that id with dash raises ValueError."""
        with pytest.raises(ValueError, match="not a valid id"):
            validate_id("my-id")

    def test_invalid_contains_space(self) -> None:
        """Test that id with space raises ValueError."""
        with pytest.raises(ValueError, match="not a valid id"):
            validate_id("my id")

    def test_invalid_contains_period(self) -> None:
        """Test that id with period in middle raises ValueError."""
        with pytest.raises(ValueError, match="not a valid id"):
            validate_id("my.id")

    def test_invalid_non_string(self) -> None:
        """Test that non-string raises ValueError."""
        with pytest.raises(ValueError, match="must be a single string"):
            validate_id(123)  # type: ignore


class TestResolveId:
    """Tests for resolve_id function."""

    def test_resolve_id_simple(self) -> None:
        """Test resolving simple id outside namespace."""
        result = resolve_id("myId")
        assert str(result) == "myId"
        assert isinstance(result, ResolvedId)

    def test_resolve_id_with_namespace(self) -> None:
        """Test resolving id within namespace context."""
        with namespace_context("ns"):
            result = resolve_id("myId")
            assert str(result) == "ns-myId"

    def test_resolve_id_already_resolved(self) -> None:
        """Test that already resolved id is returned as-is."""
        resolved = ResolvedId("already-resolved")
        result = resolve_id(resolved)
        assert result is resolved


class TestResolveIdOrNone:
    """Tests for resolve_id_or_none function."""

    def test_resolve_id_or_none_with_id(self) -> None:
        """Test resolve_id_or_none with a valid id."""
        result = resolve_id_or_none("myId")
        assert str(result) == "myId"
        assert isinstance(result, ResolvedId)

    def test_resolve_id_or_none_with_none(self) -> None:
        """Test resolve_id_or_none with None."""
        result = resolve_id_or_none(None)
        assert result is None

    def test_resolve_id_or_none_with_namespace(self) -> None:
        """Test resolve_id_or_none within namespace."""
        with namespace_context("ns"):
            result = resolve_id_or_none("myId")
            assert str(result) == "ns-myId"


class TestCurrentNamespace:
    """Tests for current_namespace function."""

    def test_current_namespace_default(self) -> None:
        """Test current namespace is Root by default."""
        result = current_namespace()
        assert result is Root

    def test_current_namespace_in_context(self) -> None:
        """Test current namespace within context."""
        with namespace_context("myns"):
            result = current_namespace()
            assert str(result) == "myns"


class TestNamespaceContext:
    """Tests for namespace_context context manager."""

    def test_namespace_context_sets_namespace(self) -> None:
        """Test that namespace_context sets the namespace."""
        with namespace_context("test"):
            assert str(current_namespace()) == "test"

    def test_namespace_context_restores_namespace(self) -> None:
        """Test that namespace_context restores previous namespace."""
        original = current_namespace()
        with namespace_context("test"):
            pass
        assert current_namespace() is original

    def test_namespace_context_nested(self) -> None:
        """Test nested namespace contexts append namespaces."""
        with namespace_context("outer"):
            assert str(current_namespace()) == "outer"
            with namespace_context("inner"):
                # Nested contexts append to form "outer-inner"
                assert str(current_namespace()) == "outer-inner"
            assert str(current_namespace()) == "outer"

    def test_namespace_context_with_none(self) -> None:
        """Test namespace_context with None uses Root."""
        with namespace_context(None):
            assert current_namespace() is Root

    def test_namespace_context_exception_restores(self) -> None:
        """Test that namespace is restored even with exception."""
        original = current_namespace()
        try:
            with namespace_context("test"):
                raise ValueError("test error")
        except ValueError:
            pass
        assert current_namespace() is original
