"""Tests for reactive teardown behavior."""

from shiny.reactive import DestroyedReactiveError


def test_destroyed_reactive_error_is_exception():
    assert issubclass(DestroyedReactiveError, Exception)
    err = DestroyedReactiveError("test message")
    assert str(err) == "test message"
