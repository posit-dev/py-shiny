"""Tests for shiny/_namespaces.py module."""

from shiny._namespaces import (
    ResolvedId,
    namespace_context,
)


class TestResolvedId:
    """Tests for ResolvedId class."""

    def test_resolved_id_exists(self):
        """Test ResolvedId exists."""
        assert ResolvedId is not None

    def test_resolved_id_is_subclass_of_str(self):
        """Test ResolvedId is a subclass of str."""
        assert issubclass(ResolvedId, str)


class TestNamespaceContext:
    """Tests for namespace_context."""

    def test_namespace_context_exists(self):
        """Test namespace_context exists."""
        assert namespace_context is not None
