"""Tests for shiny/session/__init__.py - Session module exports."""

from shiny import session


class TestSessionExports:
    """Tests for session module exports."""

    def test_session_exported(self):
        """Test Session is exported."""
        assert hasattr(session, "Session")

    def test_inputs_exported(self):
        """Test Inputs is exported."""
        assert hasattr(session, "Inputs")

    def test_outputs_exported(self):
        """Test Outputs is exported."""
        assert hasattr(session, "Outputs")

    def test_clientdata_exported(self):
        """Test ClientData is exported."""
        assert hasattr(session, "ClientData")

    def test_get_current_session_exported(self):
        """Test get_current_session is exported."""
        assert hasattr(session, "get_current_session")
        assert callable(session.get_current_session)

    def test_require_active_session_exported(self):
        """Test require_active_session is exported."""
        assert hasattr(session, "require_active_session")
        assert callable(session.require_active_session)


class TestSessionAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(session.__all__, tuple)

    def test_all_contains_session(self):
        """Test __all__ contains Session."""
        assert "Session" in session.__all__

    def test_all_contains_inputs(self):
        """Test __all__ contains Inputs."""
        assert "Inputs" in session.__all__

    def test_all_contains_outputs(self):
        """Test __all__ contains Outputs."""
        assert "Outputs" in session.__all__

    def test_all_contains_clientdata(self):
        """Test __all__ contains ClientData."""
        assert "ClientData" in session.__all__

    def test_all_contains_get_current_session(self):
        """Test __all__ contains get_current_session."""
        assert "get_current_session" in session.__all__

    def test_all_contains_require_active_session(self):
        """Test __all__ contains require_active_session."""
        assert "require_active_session" in session.__all__


class TestGetCurrentSession:
    """Tests for get_current_session function."""

    def test_returns_none_when_no_session(self):
        """Test returns None when no active session."""
        result = session.get_current_session()
        assert result is None
