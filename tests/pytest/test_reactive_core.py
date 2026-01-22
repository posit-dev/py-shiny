"""Tests for shiny/reactive/_core.py and _reactives.py modules."""

from shiny.reactive._core import (
    flush,
    invalidate_later,
    isolate,
    lock,
)
from shiny.reactive._reactives import Calc_ as Calc
from shiny.reactive._reactives import Effect_ as Effect
from shiny.reactive._reactives import (
    calc,
    effect,
)


class TestEffect:
    """Tests for reactive.effect decorator."""

    def test_effect_is_callable(self):
        """Test effect is callable."""
        assert callable(effect)


class TestEffectClass:
    """Tests for Effect class."""

    def test_effect_class_exists(self):
        """Test Effect class exists."""
        assert Effect is not None


class TestCalc:
    """Tests for reactive.calc decorator."""

    def test_calc_is_callable(self):
        """Test calc is callable."""
        assert callable(calc)


class TestCalcClass:
    """Tests for Calc class."""

    def test_calc_class_exists(self):
        """Test Calc class exists."""
        assert Calc is not None


class TestIsolate:
    """Tests for reactive.isolate context manager."""

    def test_isolate_is_callable(self):
        """Test isolate is callable."""
        assert callable(isolate)


class TestInvalidateLater:
    """Tests for reactive.invalidate_later function."""

    def test_invalidate_later_is_callable(self):
        """Test invalidate_later is callable."""
        assert callable(invalidate_later)


class TestFlush:
    """Tests for reactive.flush function."""

    def test_flush_is_callable(self):
        """Test flush is callable."""
        assert callable(flush)


class TestLock:
    """Tests for reactive.lock context manager."""

    def test_lock_is_callable(self):
        """Test lock is callable."""
        assert callable(lock)


class TestReactiveCoreExported:
    """Tests for reactive core functions export."""

    def test_effect_in_reactive(self):
        """Test effect is in reactive module."""
        from shiny import reactive

        assert hasattr(reactive, "effect")

    def test_calc_in_reactive(self):
        """Test calc is in reactive module."""
        from shiny import reactive

        assert hasattr(reactive, "calc")

    def test_isolate_in_reactive(self):
        """Test isolate is in reactive module."""
        from shiny import reactive

        assert hasattr(reactive, "isolate")

    def test_invalidate_later_in_reactive(self):
        """Test invalidate_later is in reactive module."""
        from shiny import reactive

        assert hasattr(reactive, "invalidate_later")

    def test_flush_in_reactive(self):
        """Test flush is in reactive module."""
        from shiny import reactive

        assert hasattr(reactive, "flush")
