"""Tests for the R Shiny-style concurrency model."""

from shiny.session._session import OutBoundMessageQueues


# =============================================================================
# OutBoundMessageQueues.is_empty()
# =============================================================================


def test_omq_is_empty_when_newly_created():
    """Freshly constructed OMQ reports empty."""
    omq = OutBoundMessageQueues()
    assert omq.is_empty() is True


def test_omq_is_empty_false_when_value_added():
    omq = OutBoundMessageQueues()
    omq.set_value("x", 1)
    assert omq.is_empty() is False


def test_omq_is_empty_false_when_error_added():
    omq = OutBoundMessageQueues()
    omq.set_error("x", {"message": "oops"})
    assert omq.is_empty() is False


def test_omq_is_empty_false_when_input_message_added():
    omq = OutBoundMessageQueues()
    omq.add_input_message("x", {"type": "update", "value": 1})
    assert omq.is_empty() is False


def test_omq_is_empty_after_reset():
    omq = OutBoundMessageQueues()
    omq.set_value("x", 1)
    omq.reset()
    assert omq.is_empty() is True
