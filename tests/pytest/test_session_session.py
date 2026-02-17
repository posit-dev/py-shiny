"""Tests for shiny/session/_session.py module."""

from shiny.session._session import (
    Session,
)


class TestSession:
    """Tests for Session class."""

    def test_session_class_exists(self):
        """Test Session class exists."""
        assert Session is not None

    def test_session_is_type(self):
        """Test Session is a class."""
        assert isinstance(Session, type)


class TestSessionExported:
    """Tests for session class export."""

    def test_session_in_shiny(self):
        """Test Session is in shiny module."""
        from shiny import Session as ShinySession

        assert ShinySession is not None
