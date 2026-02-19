"""
Tests for user-facing OpenTelemetry API (otel_collect context manager and decorator).
"""

import pytest

from shiny.otel import OtelCollectLevel, otel_collect, should_otel_collect
from shiny.otel._collect import get_otel_collect_level
from shiny.otel._decorators import no_otel_collect

from .otel_helpers import patch_otel_tracing_state


class TestOtelCollectContextManager:
    """Tests for otel_collect as a context manager."""

    def test_context_manager_with_string_level(self):
        """Test context manager with string level argument."""
        with patch_otel_tracing_state(tracing_enabled=True):
            # Default should be ALL (from env var or default)
            assert get_otel_collect_level() >= OtelCollectLevel.REACTIVITY

            with otel_collect("none"):
                assert get_otel_collect_level() == OtelCollectLevel.NONE
                assert not should_otel_collect(OtelCollectLevel.SESSION)

            # Should restore after context
            assert get_otel_collect_level() >= OtelCollectLevel.REACTIVITY

    def test_context_manager_with_session_level(self):
        """Test context manager with session level string."""
        with patch_otel_tracing_state(tracing_enabled=True):
            with otel_collect("session"):
                assert get_otel_collect_level() == OtelCollectLevel.SESSION
                assert should_otel_collect(OtelCollectLevel.SESSION)
                assert not should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE)

    def test_nested_context_managers(self):
        """Test nested context managers work correctly."""
        with patch_otel_tracing_state(tracing_enabled=True):
            with otel_collect("session"):
                assert get_otel_collect_level() == OtelCollectLevel.SESSION

                with otel_collect("none"):
                    assert get_otel_collect_level() == OtelCollectLevel.NONE

                    with otel_collect("all"):
                        assert get_otel_collect_level() == OtelCollectLevel.ALL

                    # Back to none
                    assert get_otel_collect_level() == OtelCollectLevel.NONE

                # Back to session
                assert get_otel_collect_level() == OtelCollectLevel.SESSION

            # Back to original
            assert get_otel_collect_level() >= OtelCollectLevel.REACTIVITY

    def test_context_manager_exception_handling(self):
        """Test context manager restores level even on exception."""
        with patch_otel_tracing_state(tracing_enabled=True):
            original_level = get_otel_collect_level()

            with pytest.raises(ValueError):
                with otel_collect("none"):
                    assert get_otel_collect_level() == OtelCollectLevel.NONE
                    raise ValueError("Test exception")

            # Should restore despite exception
            assert get_otel_collect_level() == original_level

    def test_all_string_levels(self):
        """Test all valid string level values."""
        with patch_otel_tracing_state(tracing_enabled=True):
            # Explicitly test each level to maintain type safety
            with otel_collect("none"):
                assert get_otel_collect_level() == OtelCollectLevel.NONE
            with otel_collect("session"):
                assert get_otel_collect_level() == OtelCollectLevel.SESSION
            with otel_collect("reactive_update"):
                assert get_otel_collect_level() == OtelCollectLevel.REACTIVE_UPDATE
            with otel_collect("reactivity"):
                assert get_otel_collect_level() == OtelCollectLevel.REACTIVITY
            with otel_collect("all"):
                assert get_otel_collect_level() == OtelCollectLevel.ALL

    def test_case_insensitive_strings(self):
        """Test string levels are case-insensitive at runtime."""
        with patch_otel_tracing_state(tracing_enabled=True):
            # Test various cases - type checker enforces lowercase, but runtime accepts any case
            with otel_collect("none"):
                assert get_otel_collect_level() == OtelCollectLevel.NONE
            with otel_collect("NONE"):  # type: ignore[arg-type]
                assert get_otel_collect_level() == OtelCollectLevel.NONE
            with otel_collect("None"):  # type: ignore[arg-type]
                assert get_otel_collect_level() == OtelCollectLevel.NONE
            with otel_collect("NoNe"):  # type: ignore[arg-type]
                assert get_otel_collect_level() == OtelCollectLevel.NONE

    def test_invalid_level_type_raises_error(self):
        """Test that invalid level types raise TypeError."""
        with patch_otel_tracing_state(tracing_enabled=True):
            # Test invalid types
            with pytest.raises(TypeError, match="level must be a string"):
                with otel_collect(123):  # type: ignore[arg-type]
                    pass

            with pytest.raises(TypeError, match="level must be a string"):
                with otel_collect(None):  # type: ignore[arg-type]
                    pass

            with pytest.raises(TypeError, match="level must be a string"):
                with otel_collect([]):  # type: ignore[arg-type]
                    pass


class TestOtelCollectDecorator:
    """Tests for otel_collect as a decorator."""

    def test_decorator_on_function(self):
        """Test decorator marks a function with collection level attribute."""
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL

        @otel_collect("none")
        def decorated_func():
            return "result"

        # Function should be marked with the attribute
        assert hasattr(decorated_func, FUNC_ATTR_OTEL_COLLECT_LEVEL)
        assert getattr(decorated_func, FUNC_ATTR_OTEL_COLLECT_LEVEL) == OtelCollectLevel.NONE

        # Function should still work normally
        result = decorated_func()
        assert result == "result"

    def test_decorator_with_arguments(self):
        """Test decorator marks function with arguments."""
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL

        @otel_collect("session")
        def add(a: int, b: int) -> int:  # type: ignore[misc]
            return a + b

        # Function should be marked with the attribute
        assert hasattr(add, FUNC_ATTR_OTEL_COLLECT_LEVEL)
        assert getattr(add, FUNC_ATTR_OTEL_COLLECT_LEVEL) == OtelCollectLevel.SESSION

        # Function should still work normally
        result = add(2, 3)
        assert result == 5

    def test_decorator_with_kwargs(self):
        """Test decorator marks function with keyword arguments."""
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL

        @otel_collect("none")
        def func_with_kwargs(a: int, b: int = 10, *, c: int = 20) -> int:  # type: ignore[misc]
            return a + b + c

        # Function should be marked with the attribute
        assert hasattr(func_with_kwargs, FUNC_ATTR_OTEL_COLLECT_LEVEL)
        assert getattr(func_with_kwargs, FUNC_ATTR_OTEL_COLLECT_LEVEL) == OtelCollectLevel.NONE

        # Function should still work normally
        result = func_with_kwargs(1, b=2, c=3)
        assert result == 6

    def test_decorator_preserves_function_metadata(self):
        """Test decorator preserves function name and docstring."""

        @otel_collect("none")
        def my_function():
            """My docstring."""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."

    def test_decorator_preserves_exceptions(self):
        """Test decorator doesn't interfere with exception handling."""
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL

        @otel_collect("none")
        def failing_func():
            raise ValueError("Test exception")

        # Function should be marked with the attribute
        assert hasattr(failing_func, FUNC_ATTR_OTEL_COLLECT_LEVEL)
        assert getattr(failing_func, FUNC_ATTR_OTEL_COLLECT_LEVEL) == OtelCollectLevel.NONE

        # Exception should propagate normally
        with pytest.raises(ValueError, match="Test exception"):
            failing_func()

    def test_nested_decorated_functions(self):
        """Test calling decorated function from another decorated function."""
        with patch_otel_tracing_state(tracing_enabled=True):

            @otel_collect("none")
            def inner():
                assert get_otel_collect_level() == OtelCollectLevel.NONE
                return "inner"

            @otel_collect("session")
            def outer():
                assert get_otel_collect_level() == OtelCollectLevel.SESSION
                result = inner()
                # Should restore to SESSION after inner() returns
                assert get_otel_collect_level() == OtelCollectLevel.SESSION
                return result

            result = outer()
            assert result == "inner"


class TestOtelCollectEnvironmentVariable:
    """Tests for SHINY_OTEL_COLLECT environment variable."""

    def test_env_var_sets_default_level(self, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        """Test environment variable sets default collection level."""
        with patch_otel_tracing_state(tracing_enabled=True):
            monkeypatch.setenv("SHINY_OTEL_COLLECT", "session")  # type: ignore[attr-defined]

            # Force re-read of env var by clearing contextvar
            from shiny.otel._collect import _current_collect_level

            _current_collect_level.set(None)

            assert get_otel_collect_level() == OtelCollectLevel.SESSION

    def test_context_manager_overrides_env_var(self, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        """Test context manager overrides environment variable."""
        with patch_otel_tracing_state(tracing_enabled=True):
            monkeypatch.setenv("SHINY_OTEL_COLLECT", "session")  # type: ignore[attr-defined]

            # Force re-read of env var
            from shiny.otel._collect import _current_collect_level

            _current_collect_level.set(None)

            # Env var should set to SESSION
            assert get_otel_collect_level() == OtelCollectLevel.SESSION

            # Context manager should override
            with otel_collect("none"):
                assert get_otel_collect_level() == OtelCollectLevel.NONE

            # Should restore to env var value
            assert get_otel_collect_level() == OtelCollectLevel.SESSION

    def test_invalid_env_var_defaults_with_warning(self, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        """Test invalid environment variable value defaults to ALL with warning."""
        with patch_otel_tracing_state(tracing_enabled=True):
            monkeypatch.setenv("SHINY_OTEL_COLLECT", "invalid_level")  # type: ignore[attr-defined]

            # Force re-read of env var
            from shiny.otel._collect import _current_collect_level

            _current_collect_level.set(None)

            # Should default to ALL and emit a warning
            with pytest.warns(UserWarning, match="Invalid SHINY_OTEL_COLLECT"):
                level = get_otel_collect_level()
                assert level == OtelCollectLevel.ALL


class TestOtelCollectIntegration:
    """Integration tests for otel_collect with reactive system."""

    def test_collection_level_affects_should_otel_collect(self):
        """Test that collection level affects should_otel_collect checks."""
        with patch_otel_tracing_state(tracing_enabled=True):
            # At ALL level, all checks should pass (except NONE which is invalid)
            with otel_collect("all"):
                assert should_otel_collect(OtelCollectLevel.SESSION)
                assert should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE)
                assert should_otel_collect(OtelCollectLevel.REACTIVITY)
                assert should_otel_collect(OtelCollectLevel.ALL)

            # At SESSION level, only SESSION should collect
            with otel_collect("session"):
                assert should_otel_collect(OtelCollectLevel.SESSION)
                assert not should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE)
                assert not should_otel_collect(OtelCollectLevel.REACTIVITY)
                assert not should_otel_collect(OtelCollectLevel.ALL)

            # At NONE level, nothing should collect
            with otel_collect("none"):
                assert not should_otel_collect(OtelCollectLevel.SESSION)
                assert not should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE)
                assert not should_otel_collect(OtelCollectLevel.REACTIVITY)
                assert not should_otel_collect(OtelCollectLevel.ALL)

    def test_tracing_disabled_overrides_collection_level(self):
        """Test that disabled tracing overrides collection level."""
        with patch_otel_tracing_state(tracing_enabled=False):
            # Even at ALL level, should not collect if tracing disabled
            with otel_collect("all"):
                assert not should_otel_collect(OtelCollectLevel.SESSION)
                assert not should_otel_collect(OtelCollectLevel.REACTIVE_UPDATE)
                assert not should_otel_collect(OtelCollectLevel.REACTIVITY)


class TestNoOtelCollect:
    """Tests for no_otel_collect() convenience function."""

    def test_no_otel_collect_as_context_manager(self):
        """Test no_otel_collect() works as context manager."""
        with patch_otel_tracing_state(tracing_enabled=True):
            # Should be at default level outside
            assert get_otel_collect_level() >= OtelCollectLevel.REACTIVITY

            with no_otel_collect():
                # Should be at NONE level inside
                assert get_otel_collect_level() == OtelCollectLevel.NONE
                assert not should_otel_collect(OtelCollectLevel.SESSION)

            # Should restore after context
            assert get_otel_collect_level() >= OtelCollectLevel.REACTIVITY

    def test_no_otel_collect_as_decorator(self):
        """Test no_otel_collect() works as decorator."""
        with patch_otel_tracing_state(tracing_enabled=True):

            @no_otel_collect()
            def sensitive_func() -> str:  # type: ignore[misc]
                assert get_otel_collect_level() == OtelCollectLevel.NONE
                return "secret"

            # Outside should be default
            assert get_otel_collect_level() >= OtelCollectLevel.REACTIVITY

            # Call function
            result = sensitive_func()
            assert result == "secret"

            # After should be default
            assert get_otel_collect_level() >= OtelCollectLevel.REACTIVITY

    def test_no_otel_collect_equivalent_to_otel_collect_none(self):
        """Test that no_otel_collect() is equivalent to otel_collect('none')."""
        with patch_otel_tracing_state(tracing_enabled=True):
            # Both should set level to NONE
            with no_otel_collect():
                level1 = get_otel_collect_level()

            with otel_collect("none"):
                level2 = get_otel_collect_level()

            assert level1 == level2 == OtelCollectLevel.NONE

    def test_no_otel_collect_nested(self):
        """Test no_otel_collect() can be nested."""
        with patch_otel_tracing_state(tracing_enabled=True):
            with otel_collect("session"):
                assert get_otel_collect_level() == OtelCollectLevel.SESSION

                with no_otel_collect():
                    assert get_otel_collect_level() == OtelCollectLevel.NONE

                # Back to session
                assert get_otel_collect_level() == OtelCollectLevel.SESSION
