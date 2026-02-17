"""Tests for shiny/reactive/__init__.py - Reactive module exports."""

from shiny import reactive


class TestReactiveExports:
    """Tests for reactive module exports."""

    def test_context_exported(self):
        """Test Context is exported."""
        assert hasattr(reactive, "Context")

    def test_isolate_exported(self):
        """Test isolate is exported."""
        assert hasattr(reactive, "isolate")
        assert callable(reactive.isolate)

    def test_invalidate_later_exported(self):
        """Test invalidate_later is exported."""
        assert hasattr(reactive, "invalidate_later")
        assert callable(reactive.invalidate_later)

    def test_flush_exported(self):
        """Test flush is exported."""
        assert hasattr(reactive, "flush")
        assert callable(reactive.flush)

    def test_lock_exported(self):
        """Test lock is exported."""
        assert hasattr(reactive, "lock")

    def test_on_flushed_exported(self):
        """Test on_flushed is exported."""
        assert hasattr(reactive, "on_flushed")
        assert callable(reactive.on_flushed)

    def test_poll_exported(self):
        """Test poll is exported."""
        assert hasattr(reactive, "poll")
        assert callable(reactive.poll)

    def test_file_reader_exported(self):
        """Test file_reader is exported."""
        assert hasattr(reactive, "file_reader")
        assert callable(reactive.file_reader)

    def test_value_exported(self):
        """Test value is exported."""
        assert hasattr(reactive, "value")
        assert callable(reactive.value)

    def test_value_class_exported(self):
        """Test Value class is exported."""
        assert hasattr(reactive, "Value")

    def test_calc_exported(self):
        """Test calc is exported."""
        assert hasattr(reactive, "calc")
        assert callable(reactive.calc)

    def test_calc_class_exported(self):
        """Test Calc class is exported."""
        assert hasattr(reactive, "Calc")

    def test_effect_exported(self):
        """Test effect is exported."""
        assert hasattr(reactive, "effect")
        assert callable(reactive.effect)

    def test_effect_class_exported(self):
        """Test Effect class is exported."""
        assert hasattr(reactive, "Effect")

    def test_event_exported(self):
        """Test event is exported."""
        assert hasattr(reactive, "event")
        assert callable(reactive.event)

    def test_extended_task_exported(self):
        """Test ExtendedTask is exported."""
        assert hasattr(reactive, "ExtendedTask")

    def test_extended_task_decorator_exported(self):
        """Test extended_task decorator is exported."""
        assert hasattr(reactive, "extended_task")
        assert callable(reactive.extended_task)


class TestReactiveAll:
    """Tests for __all__ exports."""

    def test_all_contains_context(self):
        """Test __all__ contains Context."""
        assert "Context" in reactive.__all__

    def test_all_contains_isolate(self):
        """Test __all__ contains isolate."""
        assert "isolate" in reactive.__all__

    def test_all_contains_invalidate_later(self):
        """Test __all__ contains invalidate_later."""
        assert "invalidate_later" in reactive.__all__

    def test_all_contains_flush(self):
        """Test __all__ contains flush."""
        assert "flush" in reactive.__all__

    def test_all_contains_lock(self):
        """Test __all__ contains lock."""
        assert "lock" in reactive.__all__

    def test_all_contains_on_flushed(self):
        """Test __all__ contains on_flushed."""
        assert "on_flushed" in reactive.__all__

    def test_all_contains_poll(self):
        """Test __all__ contains poll."""
        assert "poll" in reactive.__all__

    def test_all_contains_file_reader(self):
        """Test __all__ contains file_reader."""
        assert "file_reader" in reactive.__all__

    def test_all_contains_value(self):
        """Test __all__ contains value."""
        assert "value" in reactive.__all__

    def test_all_contains_value_class(self):
        """Test __all__ contains Value."""
        assert "Value" in reactive.__all__

    def test_all_contains_calc(self):
        """Test __all__ contains calc."""
        assert "calc" in reactive.__all__

    def test_all_contains_calc_class(self):
        """Test __all__ contains Calc."""
        assert "Calc" in reactive.__all__

    def test_all_contains_effect(self):
        """Test __all__ contains effect."""
        assert "effect" in reactive.__all__

    def test_all_contains_effect_class(self):
        """Test __all__ contains Effect."""
        assert "Effect" in reactive.__all__

    def test_all_contains_event(self):
        """Test __all__ contains event."""
        assert "event" in reactive.__all__

    def test_all_contains_extended_task(self):
        """Test __all__ contains ExtendedTask."""
        assert "ExtendedTask" in reactive.__all__

    def test_all_contains_extended_task_decorator(self):
        """Test __all__ contains extended_task."""
        assert "extended_task" in reactive.__all__
