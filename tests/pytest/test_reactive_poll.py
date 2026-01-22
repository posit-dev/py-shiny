"""Tests for shiny/reactive/_poll.py module."""

from shiny.reactive._poll import (
    poll,
    file_reader,
)


class TestPoll:
    """Tests for reactive.poll function."""

    def test_poll_is_callable(self):
        """Test poll is callable."""
        assert callable(poll)


class TestFileReader:
    """Tests for reactive.file_reader function."""

    def test_file_reader_is_callable(self):
        """Test file_reader is callable."""
        assert callable(file_reader)


class TestPollExported:
    """Tests for poll functions export."""

    def test_poll_in_reactive(self):
        """Test poll is in reactive module."""
        from shiny import reactive

        assert hasattr(reactive, "poll")

    def test_file_reader_in_reactive(self):
        """Test file_reader is in reactive module."""
        from shiny import reactive

        assert hasattr(reactive, "file_reader")
