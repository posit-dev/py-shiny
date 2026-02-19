"""
Tests for otel_collect() function and OpenTelemetry collection control.

Tests cover:
- otel_collect() as context manager and decorator
- Environment variable configuration (SHINY_OTEL_COLLECT)
- Integration with reactive primitives (Value, Calc_, Effect_, Renderer)
- Validation and error handling
"""

import pytest

from shiny.otel import otel_collect
from shiny.otel._collect import OtelCollectLevel, get_otel_collect_level
from shiny.otel._core import is_otel_tracing_enabled
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
                assert not (
                    is_otel_tracing_enabled()
                    and get_otel_collect_level() >= OtelCollectLevel.SESSION
                )

            # Should restore after context
            assert get_otel_collect_level() >= OtelCollectLevel.REACTIVITY

    def test_context_manager_with_session_level(self):
        """Test context manager with session level string."""
        with patch_otel_tracing_state(tracing_enabled=True):
            with otel_collect("session"):
                assert get_otel_collect_level() == OtelCollectLevel.SESSION
                assert (
                    is_otel_tracing_enabled()
                    and get_otel_collect_level() >= OtelCollectLevel.SESSION
                )
                assert not (
                    is_otel_tracing_enabled()
                    and get_otel_collect_level() >= OtelCollectLevel.REACTIVE_UPDATE
                )

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

    def test_case_sensitive_strings(self):
        """Test string levels must be lowercase (enforced at runtime)."""
        with patch_otel_tracing_state(tracing_enabled=True):
            # Lowercase should work (matches Literal type hint)
            with otel_collect("none"):
                assert get_otel_collect_level() == OtelCollectLevel.NONE

            # Non-lowercase should raise ValueError
            with pytest.raises(ValueError, match="must be lowercase"):
                with otel_collect("NONE"):  # type: ignore[arg-type]
                    pass

            with pytest.raises(ValueError, match="must be lowercase"):
                with otel_collect("None"):  # type: ignore[arg-type]
                    pass

            with pytest.raises(ValueError, match="must be lowercase"):
                with otel_collect("NoNe"):  # type: ignore[arg-type]
                    pass

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
        assert (
            getattr(decorated_func, FUNC_ATTR_OTEL_COLLECT_LEVEL)
            == OtelCollectLevel.NONE
        )

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
        assert (
            getattr(func_with_kwargs, FUNC_ATTR_OTEL_COLLECT_LEVEL)
            == OtelCollectLevel.NONE
        )

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
        assert (
            getattr(failing_func, FUNC_ATTR_OTEL_COLLECT_LEVEL) == OtelCollectLevel.NONE
        )

        # Exception should propagate normally
        with pytest.raises(ValueError, match="Test exception"):
            failing_func()

    def test_nested_decorated_functions(self):
        """Test multiple functions can be decorated with different levels."""
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL

        @otel_collect("none")
        def inner():
            return "inner"

        @otel_collect("session")
        def outer():
            result = inner()
            return result

        # Both functions should be marked with their respective attributes
        assert hasattr(inner, FUNC_ATTR_OTEL_COLLECT_LEVEL)
        assert getattr(inner, FUNC_ATTR_OTEL_COLLECT_LEVEL) == OtelCollectLevel.NONE

        assert hasattr(outer, FUNC_ATTR_OTEL_COLLECT_LEVEL)
        assert getattr(outer, FUNC_ATTR_OTEL_COLLECT_LEVEL) == OtelCollectLevel.SESSION

        # Functions should work normally
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
                assert not (
                    is_otel_tracing_enabled()
                    and get_otel_collect_level() >= OtelCollectLevel.SESSION
                )

            # Should restore after context
            assert get_otel_collect_level() >= OtelCollectLevel.REACTIVITY

    def test_no_otel_collect_as_decorator(self):
        """Test no_otel_collect() marks function with NONE collection level."""
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL

        @no_otel_collect()
        def sensitive_func() -> str:  # type: ignore[misc]
            return "secret"

        # Function should be marked with NONE level attribute
        assert hasattr(sensitive_func, FUNC_ATTR_OTEL_COLLECT_LEVEL)
        assert (
            getattr(sensitive_func, FUNC_ATTR_OTEL_COLLECT_LEVEL)
            == OtelCollectLevel.NONE
        )

        # Function should still work normally
        result = sensitive_func()
        assert result == "secret"

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


class TestOtelCollectIntegrationWithRealBackend:
    """Integration tests using real OpenTelemetry exporters (not mocks).

    These tests verify that otel_collect controls the decision to create spans,
    though we test synchronously due to context variable propagation limitations
    with asyncio.run().
    """

    def test_reactive_value_captures_collect_level_at_init(self):
        """Verify reactive Value captures collect level at initialization."""
        from shiny import reactive

        from .otel_helpers import patch_otel_tracing_state

        with patch_otel_tracing_state(tracing_enabled=True):
            # Create value with NONE level - it should remember this
            with otel_collect("none"):
                val_none = reactive.value(0)
                # Access internal _otel_level attribute to verify it was captured
                assert val_none._otel_level == OtelCollectLevel.NONE

            # Create value with ALL level - it should remember this
            with otel_collect("all"):
                val_all = reactive.value(100)
                assert val_all._otel_level == OtelCollectLevel.ALL

            # Values should remember their initialization levels
            # even after context exits
            assert val_none._otel_level == OtelCollectLevel.NONE
            assert val_all._otel_level == OtelCollectLevel.ALL

    def test_decorator_marks_function_with_collect_level(self):
        """Verify @otel_collect decorator marks functions with collect level."""
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL
        from shiny.otel._function_attrs import resolve_func_otel_level

        # Decorated function should have the attribute
        @otel_collect("none")
        def func_none():
            pass

        assert hasattr(func_none, FUNC_ATTR_OTEL_COLLECT_LEVEL)
        assert resolve_func_otel_level(func_none) == OtelCollectLevel.NONE

        # Different level
        @otel_collect("reactivity")
        def func_reactivity():
            pass

        assert resolve_func_otel_level(func_reactivity) == OtelCollectLevel.REACTIVITY

    def test_calc_and_effect_capture_decorator_level(self):
        """Verify Calc_ and Effect_ capture decorator collect level."""
        from shiny import reactive

        from .otel_helpers import patch_otel_tracing_state

        with patch_otel_tracing_state(tracing_enabled=True):
            # Correct decorator order: @reactive.calc AFTER @otel_collect
            # so the function is marked first, then wrapped
            @reactive.calc
            @otel_collect("none")
            def my_calc():
                return 42

            # Access internal _otel_level to verify it was captured
            assert my_calc._otel_level == OtelCollectLevel.NONE

            @reactive.effect
            @otel_collect("reactivity")
            def my_effect():
                pass

            assert my_effect._otel_level == OtelCollectLevel.REACTIVITY

    def test_otel_collect_rejects_calc_objects(self):
        """Verify otel_collect rejects already-wrapped Calc_ objects."""
        from shiny import reactive

        # Create a calc first
        @reactive.calc
        def my_calc():
            return 42

        # Trying to apply otel_collect to the Calc_ object should fail
        with pytest.raises(TypeError, match="cannot be used on @reactive.calc objects"):
            otel_collect("none")(my_calc)

    def test_otel_collect_rejects_effect_objects(self):
        """Verify otel_collect rejects already-wrapped Effect_ objects."""
        from shiny import reactive

        # Create an effect first
        @reactive.effect
        def my_effect():
            pass

        # Trying to apply otel_collect to the Effect_ object should fail
        with pytest.raises(
            TypeError, match="cannot be used on @reactive.effect objects"
        ):
            otel_collect("none")(my_effect)  # pyright: ignore[reportArgumentType]

    def test_otel_collect_rejects_renderer_objects(self):
        """Verify otel_collect rejects already-wrapped Renderer objects."""
        from shiny import render

        # Create a renderer first
        @render.text
        def my_text():
            return "hello"

        # Trying to apply otel_collect to the Renderer object should fail
        with pytest.raises(TypeError, match="cannot be used on render objects"):
            otel_collect("none")(my_text)

    def test_otel_collect_accepts_plain_functions(self):
        """Verify otel_collect works on plain functions (correct usage)."""

        # This should work fine
        @otel_collect("none")
        def plain_func():
            return 42

        assert plain_func() == 42

        # This should also work (correct decorator order)
        @otel_collect("none")
        def func_to_wrap():
            return 100

        # Function should be marked before wrapping
        from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL

        assert hasattr(func_to_wrap, FUNC_ATTR_OTEL_COLLECT_LEVEL)
