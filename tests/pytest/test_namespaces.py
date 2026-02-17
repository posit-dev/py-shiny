import pytest

from shiny._namespaces import (
    ResolvedId,
    Root,
    current_namespace,
    namespace_context,
    resolve_id_or_none,
    validate_id,
)
from shiny.module import resolve_id


def test_namespaces():
    outer = resolve_id("outer")
    assert outer == "outer"

    with namespace_context(outer):
        # Check if the namespace_context ("outer") is respected during resolve_id
        inner = resolve_id("inner")
        assert inner == "outer-inner"

        # You can also use a ResolvedId as a namespace just by calling it with an id str
        assert outer("inner") == "outer-inner"

        # If an id is already resolved (based on ResolvedId class), resolving it further
        # does nothing
        assert resolve_id(outer) == "outer"

        # When namespace contexts are stacked, inner one wins
        with namespace_context(inner):
            assert resolve_id("inmost") == "outer-inner-inmost"

        # Namespace contexts nest with existing context when string is used
        with namespace_context("inner"):
            assert resolve_id("inmost") == "outer-inner-inmost"

        # Re-installing the same context as is already in place
        with namespace_context(outer):
            assert resolve_id("inmost") == "outer-inmost"

        # You can remove the context with None or ""
        with namespace_context(None):
            assert resolve_id("foo") == "foo"
        with namespace_context(""):
            assert resolve_id("foo") == "foo"

        # Check that this still works after another context was installed/removed
        assert resolve_id("inner") == "outer-inner"


class TestValidateId:
    """Tests for the validate_id function."""

    def test_valid_simple_id(self):
        """Test that simple valid IDs don't raise."""
        validate_id("myid")
        validate_id("my_id")
        validate_id("myId123")
        validate_id("_private")

    def test_valid_id_with_leading_dot(self):
        """Test that IDs starting with a dot are valid."""
        validate_id(".hidden")
        validate_id(".myId")

    def test_empty_string_raises(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="`id` must be a non-empty string"):
            validate_id("")

    def test_non_string_raises(self):
        """Test that non-string raises ValueError."""
        with pytest.raises(ValueError, match="`id` must be a single string"):
            validate_id(123)  # type: ignore

        with pytest.raises(ValueError, match="`id` must be a single string"):
            validate_id(None)  # type: ignore

    def test_invalid_characters_raise(self):
        """Test that IDs with invalid characters raise ValueError."""
        with pytest.raises(ValueError, match="is not a valid id"):
            validate_id("my-id")  # dash is not allowed

        with pytest.raises(ValueError, match="is not a valid id"):
            validate_id("my id")  # space is not allowed

        with pytest.raises(ValueError, match="is not a valid id"):
            validate_id("my.id")  # dot in middle is not allowed

        with pytest.raises(ValueError, match="is not a valid id"):
            validate_id("my,id")  # comma is not allowed


class TestResolvedId:
    """Tests for the ResolvedId class."""

    def test_resolved_id_is_string(self):
        """Test that ResolvedId is a string subclass."""
        rid = ResolvedId("test")
        assert isinstance(rid, str)
        assert rid == "test"

    def test_resolved_id_call_with_string(self):
        """Test calling ResolvedId with a string ID."""
        rid = ResolvedId("parent")
        child = rid("child")
        assert child == "parent-child"
        assert isinstance(child, ResolvedId)

    def test_resolved_id_call_with_resolved_id(self):
        """Test calling ResolvedId with another ResolvedId returns it unchanged."""
        rid = ResolvedId("parent")
        already_resolved = ResolvedId("already_resolved")
        result = rid(already_resolved)
        assert result == "already_resolved"
        assert result is already_resolved

    def test_root_resolved_id(self):
        """Test the Root ResolvedId."""
        assert Root == ""
        result = Root("child")
        assert result == "child"

    def test_empty_resolved_id(self):
        """Test that empty ResolvedId creates child without separator."""
        empty = ResolvedId("")
        child = empty("child")
        assert child == "child"


class TestResolveIdOrNone:
    """Tests for the resolve_id_or_none function."""

    def test_resolve_none_returns_none(self):
        """Test that None input returns None."""
        result = resolve_id_or_none(None)
        assert result is None

    def test_resolve_string_returns_resolved(self):
        """Test that string input returns ResolvedId."""
        result = resolve_id_or_none("myid")
        assert isinstance(result, ResolvedId)
        assert result == "myid"

    def test_resolve_in_namespace_context(self):
        """Test resolve_id_or_none respects namespace context."""
        with namespace_context("ns"):
            result = resolve_id_or_none("myid")
            assert result == "ns-myid"

            none_result = resolve_id_or_none(None)
            assert none_result is None


class TestCurrentNamespace:
    """Tests for the current_namespace function."""

    def test_default_namespace_is_root(self):
        """Test that default namespace is Root."""
        ns = current_namespace()
        assert ns == Root

    def test_namespace_in_context(self):
        """Test that current_namespace returns correct value in context."""
        with namespace_context("test"):
            ns = current_namespace()
            assert ns == "test"

    def test_nested_namespace_context(self):
        """Test nested namespace contexts."""
        with namespace_context("outer"):
            assert current_namespace() == "outer"
            with namespace_context("inner"):
                assert current_namespace() == "outer-inner"
            assert current_namespace() == "outer"
