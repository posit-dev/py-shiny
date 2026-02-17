"""Tests for shiny._typing_extensions module."""

from shiny._typing_extensions import (
    Annotated,
    Concatenate,
    Never,
    NotRequired,
    ParamSpec,
    Required,
    Self,
    TypedDict,
    TypeGuard,
    TypeIs,
    assert_type,
)


class TestTypingExtensions:
    """Tests for typing extensions exports."""

    def test_annotated_is_available(self):
        """Annotated should be available."""
        assert Annotated is not None

    def test_concatenate_is_available(self):
        """Concatenate should be available."""
        assert Concatenate is not None

    def test_param_spec_is_available(self):
        """ParamSpec should be available."""
        assert ParamSpec is not None

    def test_type_guard_is_available(self):
        """TypeGuard should be available."""
        assert TypeGuard is not None

    def test_type_is_is_available(self):
        """TypeIs should be available."""
        assert TypeIs is not None

    def test_never_is_available(self):
        """Never should be available."""
        assert Never is not None

    def test_required_is_available(self):
        """Required should be available."""
        assert Required is not None

    def test_not_required_is_available(self):
        """NotRequired should be available."""
        assert NotRequired is not None

    def test_self_is_available(self):
        """Self should be available."""
        assert Self is not None

    def test_typed_dict_is_available(self):
        """TypedDict should be available."""
        assert TypedDict is not None

    def test_assert_type_is_available(self):
        """assert_type should be available."""
        assert assert_type is not None

    def test_param_spec_can_create_instance(self):
        """ParamSpec should be usable to create parameter specs."""
        P = ParamSpec("P")
        assert P is not None
        assert P.__name__ == "P"

    def test_typed_dict_can_create_class(self):
        """TypedDict should be usable to create TypedDict classes."""

        class MyDict(TypedDict):
            name: str
            value: int

        assert MyDict is not None
        # TypedDict should have annotations
        assert hasattr(MyDict, "__annotations__")
