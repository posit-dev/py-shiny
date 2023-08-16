from shiny._namespaces import namespace_context, resolve_id


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
