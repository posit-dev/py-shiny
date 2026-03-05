"""
Tests for otel.suppress and Shiny OTel collection control.
"""

import pytest

from shiny import otel
from shiny.otel._collect import OtelCollectLevel, _current_collect_level, _get_env_level
from shiny.otel._constants import FUNC_ATTR_OTEL_COLLECT_LEVEL

from .otel_helpers import patch_otel_tracing_state


@pytest.fixture(autouse=True)
def clear_otel_collect_env(monkeypatch: pytest.MonkeyPatch):
    """Clear SHINY_OTEL_COLLECT so tests get the default (ALL) unless they set it."""
    monkeypatch.delenv("SHINY_OTEL_COLLECT", raising=False)


class TestSuppressDecorator:
    """Tests for @otel.suppress (no parens) as a function decorator."""

    def test_stamps_function_with_none_level(self):
        @otel.suppress
        def my_func():
            return 42

        assert getattr(my_func, FUNC_ATTR_OTEL_COLLECT_LEVEL) == OtelCollectLevel.NONE
        assert my_func() == 42

    def test_preserves_function_name_and_docstring(self):
        @otel.suppress
        def my_func():
            """My docstring."""
            pass

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "My docstring."

    def test_preserves_exceptions(self):
        @otel.suppress
        def failing_func():
            raise ValueError("boom")

        assert (
            getattr(failing_func, FUNC_ATTR_OTEL_COLLECT_LEVEL) == OtelCollectLevel.NONE
        )
        with pytest.raises(ValueError, match="boom"):
            failing_func()

    def test_with_parens_then_callable_raises(self):
        """@otel.suppress() with parens used as decorator should raise TypeError."""
        with pytest.raises(TypeError):
            otel.suppress()(lambda: None)  # type: ignore[misc]

    def test_rejects_calc_object(self):
        from shiny import reactive

        @reactive.calc
        def my_calc():
            return 1

        with pytest.raises(TypeError, match="@reactive.calc"):
            otel.suppress(my_calc)  # type: ignore[arg-type]

    def test_rejects_effect_object(self):
        from shiny import reactive

        @reactive.effect
        def my_effect():
            pass

        with pytest.raises(TypeError, match="@reactive.effect"):
            otel.suppress(my_effect)  # type: ignore[arg-type]

    def test_rejects_renderer_object(self):
        from shiny import render

        @render.text
        def my_text():
            return "hello"

        with pytest.raises(TypeError, match="render"):
            otel.suppress(my_text)  # type: ignore[arg-type]


class TestSuppressContextManager:
    """Tests for with otel.suppress(): as a context manager."""

    def test_sets_none_level_inside_block(self):
        with patch_otel_tracing_state(tracing_enabled=True):
            assert otel.get_level() >= OtelCollectLevel.REACTIVITY

            with otel.suppress():
                assert otel.get_level() == OtelCollectLevel.NONE

            assert otel.get_level() >= OtelCollectLevel.REACTIVITY

    def test_restores_level_after_exception(self):
        with patch_otel_tracing_state(tracing_enabled=True):
            original = otel.get_level()

            with pytest.raises(ValueError):
                with otel.suppress():
                    assert otel.get_level() == OtelCollectLevel.NONE
                    raise ValueError("boom")

            assert otel.get_level() == original

    def test_nested_suppress_contexts(self):
        with patch_otel_tracing_state(tracing_enabled=True):
            with otel.suppress():
                assert otel.get_level() == OtelCollectLevel.NONE
                with otel.suppress():
                    assert otel.get_level() == OtelCollectLevel.NONE
                assert otel.get_level() == OtelCollectLevel.NONE


class TestGetLevel:
    """Tests for otel.get_level()."""

    def test_returns_all_when_no_context_or_env(self):
        _current_collect_level.set(None)
        assert otel.get_level() == OtelCollectLevel.ALL

    def test_returns_none_inside_suppress_context(self):
        with otel.suppress():
            assert otel.get_level() == OtelCollectLevel.NONE

    def test_env_var_sets_level(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("SHINY_OTEL_COLLECT", "session")
        _current_collect_level.set(None)
        assert otel.get_level() == OtelCollectLevel.SESSION

    def test_suppress_overrides_env_var(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("SHINY_OTEL_COLLECT", "session")
        _current_collect_level.set(None)
        assert otel.get_level() == OtelCollectLevel.SESSION

        with otel.suppress():
            assert otel.get_level() == OtelCollectLevel.NONE

        assert otel.get_level() == OtelCollectLevel.SESSION

    def test_invalid_env_var_warns_and_defaults_to_all(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("SHINY_OTEL_COLLECT", "bogus")
        _current_collect_level.set(None)
        with pytest.warns(UserWarning, match="Invalid SHINY_OTEL_COLLECT"):
            assert otel.get_level() == OtelCollectLevel.ALL

    def test_get_env_level_ignores_contextvar(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("SHINY_OTEL_COLLECT", "session")
        _current_collect_level.set(None)

        with otel.suppress():
            # get_level() returns NONE (contextvar wins)
            assert otel.get_level() == OtelCollectLevel.NONE
            # _get_env_level() ignores contextvar, returns env var value
            assert _get_env_level() == OtelCollectLevel.SESSION

    def test_get_env_level_defaults_to_all(self):
        _current_collect_level.set(None)
        assert _get_env_level() == OtelCollectLevel.ALL


class TestInfrastructureSpanIsolation:
    """Infrastructure spans must not be affected by otel.suppress / otel.collect."""

    def test_get_env_level_inside_suppress_returns_env_not_none(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("SHINY_OTEL_COLLECT", "reactive_update")
        _current_collect_level.set(None)

        with otel.suppress():
            assert otel.get_level() == OtelCollectLevel.NONE
            assert _get_env_level() == OtelCollectLevel.REACTIVE_UPDATE

    def test_get_env_level_inside_collect_returns_env_not_all(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("SHINY_OTEL_COLLECT", "session")
        _current_collect_level.set(None)

        assert _get_env_level() == OtelCollectLevel.SESSION


class TestSuppressIntegration:
    """Integration tests for otel.suppress with the reactive system."""

    def test_reactive_value_captures_none_at_init(self):
        from shiny import reactive

        with patch_otel_tracing_state(tracing_enabled=True):
            with otel.suppress():
                val = reactive.value(0)
                assert val._otel_level == OtelCollectLevel.NONE

    def test_reactive_value_captures_default_outside_suppress(self):
        from shiny import reactive

        with patch_otel_tracing_state(tracing_enabled=True):
            val = reactive.value(0)
            assert val._otel_level >= OtelCollectLevel.REACTIVITY

    def test_calc_captures_suppress_level_from_decorator(self):
        from shiny import reactive

        with patch_otel_tracing_state(tracing_enabled=True):

            @reactive.calc
            @otel.suppress
            def my_calc():
                return 42

            assert my_calc._otel_level == OtelCollectLevel.NONE

    def test_effect_captures_suppress_level_from_decorator(self):
        from shiny import reactive

        with patch_otel_tracing_state(tracing_enabled=True):

            @reactive.effect
            @otel.suppress
            def my_effect():
                pass

            assert my_effect._otel_level == OtelCollectLevel.NONE

    def test_suppress_stamps_function_used_with_calc_and_effect(self):
        """Verify the function attribute is set before the reactive wrapper reads it."""
        from shiny.otel._function_attrs import resolve_func_otel_level

        @otel.suppress
        def plain_func():
            return 99

        assert resolve_func_otel_level(plain_func) == OtelCollectLevel.NONE


class TestCollectDecorator:
    """Tests for @otel.collect (no parens) as a function decorator."""

    def test_stamps_function_with_all_level(self):
        @otel.collect
        def my_func():
            return 42

        assert getattr(my_func, FUNC_ATTR_OTEL_COLLECT_LEVEL) == OtelCollectLevel.ALL
        assert my_func() == 42

    def test_preserves_function_name_and_docstring(self):
        @otel.collect
        def my_func():
            """My docstring."""
            pass

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "My docstring."

    def test_rejects_calc_object(self):
        from shiny import reactive

        @reactive.calc
        def my_calc():
            return 1

        with pytest.raises(TypeError, match="@reactive.calc"):
            otel.collect(my_calc)  # type: ignore[arg-type]

    def test_rejects_effect_object(self):
        from shiny import reactive

        @reactive.effect
        def my_effect():
            pass

        with pytest.raises(TypeError, match="@reactive.effect"):
            otel.collect(my_effect)  # type: ignore[arg-type]

    def test_rejects_renderer_object(self):
        from shiny import render

        @render.text
        def my_text():
            return "hello"

        with pytest.raises(TypeError, match="render"):
            otel.collect(my_text)  # type: ignore[arg-type]


class TestCollectContextManager:
    """Tests for with otel.collect(): as a context manager."""

    def test_sets_all_level_inside_block(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("SHINY_OTEL_COLLECT", "none")
        _current_collect_level.set(None)

        assert otel.get_level() == OtelCollectLevel.NONE

        with otel.collect():
            assert otel.get_level() == OtelCollectLevel.ALL

        assert otel.get_level() == OtelCollectLevel.NONE

    def test_restores_level_after_exception(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("SHINY_OTEL_COLLECT", "none")
        _current_collect_level.set(None)
        original = otel.get_level()

        with pytest.raises(ValueError):
            with otel.collect():
                assert otel.get_level() == OtelCollectLevel.ALL
                raise ValueError("boom")

        assert otel.get_level() == original

    def test_nested_collect_inside_suppress(self):
        with patch_otel_tracing_state(tracing_enabled=True):
            with otel.suppress():
                assert otel.get_level() == OtelCollectLevel.NONE
                with otel.collect():
                    assert otel.get_level() == OtelCollectLevel.ALL
                assert otel.get_level() == OtelCollectLevel.NONE

    def test_nested_suppress_inside_collect(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("SHINY_OTEL_COLLECT", "none")
        _current_collect_level.set(None)

        with otel.collect():
            assert otel.get_level() == OtelCollectLevel.ALL
            with otel.suppress():
                assert otel.get_level() == OtelCollectLevel.NONE
            assert otel.get_level() == OtelCollectLevel.ALL


class TestCollectIntegration:
    """Integration tests for otel.collect with the reactive system."""

    def test_reactive_value_captures_all_at_init(self, monkeypatch: pytest.MonkeyPatch):
        from shiny import reactive

        monkeypatch.setenv("SHINY_OTEL_COLLECT", "none")
        _current_collect_level.set(None)

        with patch_otel_tracing_state(tracing_enabled=True):
            with otel.collect():
                val = reactive.value(0)
                assert val._otel_level == OtelCollectLevel.ALL

    def test_calc_captures_all_level_from_decorator(self):
        from shiny import reactive

        with patch_otel_tracing_state(tracing_enabled=True):

            @reactive.calc
            @otel.collect
            def my_calc():
                return 42

            assert my_calc._otel_level == OtelCollectLevel.ALL

    def test_collect_stamps_function_used_with_calc(self):
        from shiny.otel._function_attrs import resolve_func_otel_level

        @otel.collect
        def plain_func():
            return 99

        assert resolve_func_otel_level(plain_func) == OtelCollectLevel.ALL
