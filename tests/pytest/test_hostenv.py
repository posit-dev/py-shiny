"""Tests for shiny/_hostenv.py - Host environment detection and URL proxying."""

import logging
import os
from unittest.mock import patch

from shiny._hostenv import (
    ProxyUrlFilter,
    get_proxy_url,
    is_codespaces,
    is_proxy_env,
    is_workbench,
    pat_local_url,
    port_cache,
)


class TestIsWorkbench:
    """Tests for is_workbench function."""

    def test_is_workbench_false_by_default(self):
        """Test returns False when env vars not set."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_workbench() is False

    def test_is_workbench_false_with_partial_env(self):
        """Test returns False with only one env var set."""
        with patch.dict(os.environ, {"RS_SERVER_URL": "http://server"}, clear=True):
            assert is_workbench() is False

        with patch.dict(os.environ, {"RS_SESSION_URL": "/session/"}, clear=True):
            assert is_workbench() is False

    def test_is_workbench_true_with_both_env_vars(self):
        """Test returns True when both env vars are set."""
        env = {
            "RS_SERVER_URL": "http://server",
            "RS_SESSION_URL": "/session/",
        }
        with patch.dict(os.environ, env, clear=True):
            assert is_workbench() is True


class TestIsCodespaces:
    """Tests for is_codespaces function."""

    def test_is_codespaces_false_by_default(self):
        """Test returns False when env vars not set."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_codespaces() is False

    def test_is_codespaces_false_with_partial_env(self):
        """Test returns False with incomplete env vars."""
        with patch.dict(os.environ, {"CODESPACES": "true"}, clear=True):
            assert is_codespaces() is False

        env = {"CODESPACES": "true", "CODESPACE_NAME": "myspace"}
        with patch.dict(os.environ, env, clear=True):
            assert is_codespaces() is False

    def test_is_codespaces_true_with_all_env_vars(self):
        """Test returns True when all required env vars are set."""
        env = {
            "CODESPACES": "true",
            "CODESPACE_NAME": "myspace",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "preview.app.github.dev",
        }
        with patch.dict(os.environ, env, clear=True):
            assert is_codespaces() is True


class TestIsProxyEnv:
    """Tests for is_proxy_env function."""

    def test_is_proxy_env_false_by_default(self):
        """Test returns False when not in proxy environment."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_proxy_env() is False

    def test_is_proxy_env_true_for_workbench(self):
        """Test returns True when in Workbench."""
        env = {
            "RS_SERVER_URL": "http://server",
            "RS_SESSION_URL": "/session/",
        }
        with patch.dict(os.environ, env, clear=True):
            assert is_proxy_env() is True

    def test_is_proxy_env_true_for_codespaces(self):
        """Test returns True when in Codespaces."""
        env = {
            "CODESPACES": "true",
            "CODESPACE_NAME": "myspace",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "preview.app.github.dev",
        }
        with patch.dict(os.environ, env, clear=True):
            assert is_proxy_env() is True


class TestGetProxyUrl:
    """Tests for get_proxy_url function."""

    def test_returns_url_unchanged_when_not_proxy_env(self):
        """Test URL unchanged when not in proxy environment."""
        with patch.dict(os.environ, {}, clear=True):
            url = "http://localhost:8000/app"
            assert get_proxy_url(url) == url

    def test_returns_url_unchanged_for_non_loopback(self):
        """Test non-loopback URLs are returned unchanged."""
        env = {
            "CODESPACES": "true",
            "CODESPACE_NAME": "myspace",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "preview.app.github.dev",
        }
        with patch.dict(os.environ, env, clear=True):
            url = "http://example.com:8000/app"
            assert get_proxy_url(url) == url

    def test_returns_url_unchanged_for_port_0(self):
        """Test port 0 URLs are returned unchanged."""
        env = {
            "CODESPACES": "true",
            "CODESPACE_NAME": "myspace",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "preview.app.github.dev",
        }
        with patch.dict(os.environ, env, clear=True):
            url = "http://localhost:0/app"
            assert get_proxy_url(url) == url

    def test_codespaces_proxy_url(self):
        """Test URL proxying for Codespaces."""
        env = {
            "CODESPACES": "true",
            "CODESPACE_NAME": "myspace",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "preview.app.github.dev",
        }
        with patch.dict(os.environ, env, clear=True):
            url = "http://localhost:8000/app"
            result = get_proxy_url(url)
            assert "myspace-8000" in result
            assert "preview.app.github.dev" in result
            assert "https://" in result

    def test_codespaces_proxy_url_websocket(self):
        """Test WebSocket URL proxying for Codespaces."""
        env = {
            "CODESPACES": "true",
            "CODESPACE_NAME": "myspace",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "preview.app.github.dev",
        }
        with patch.dict(os.environ, env, clear=True):
            url = "ws://localhost:8000/ws"
            result = get_proxy_url(url)
            assert "wss://" in result
            assert "myspace-8000" in result

    def test_implicit_http_port(self):
        """Test URL with implicit HTTP port 80."""
        env = {
            "CODESPACES": "true",
            "CODESPACE_NAME": "myspace",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "preview.app.github.dev",
        }
        with patch.dict(os.environ, env, clear=True):
            url = "http://localhost/app"
            result = get_proxy_url(url)
            assert "myspace-80" in result

    def test_implicit_https_port(self):
        """Test URL with implicit HTTPS port 443."""
        env = {
            "CODESPACES": "true",
            "CODESPACE_NAME": "myspace",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "preview.app.github.dev",
        }
        with patch.dict(os.environ, env, clear=True):
            url = "https://localhost/app"
            result = get_proxy_url(url)
            assert "myspace-443" in result

    def test_127_0_0_1_is_loopback(self):
        """Test that 127.0.0.1 is recognized as loopback."""
        env = {
            "CODESPACES": "true",
            "CODESPACE_NAME": "myspace",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "preview.app.github.dev",
        }
        with patch.dict(os.environ, env, clear=True):
            url = "http://127.0.0.1:8000/app"
            result = get_proxy_url(url)
            assert result != url
            assert "myspace-8000" in result


class TestPatLocalUrl:
    """Tests for the pat_local_url regex pattern."""

    def test_matches_localhost(self):
        """Test pattern matches localhost URLs."""
        assert pat_local_url.match("http://localhost:8000/path")
        assert pat_local_url.match("https://localhost/")

    def test_matches_127_0_0_1(self):
        """Test pattern matches 127.0.0.1 URLs."""
        assert pat_local_url.match("http://127.0.0.1:8000/path")
        assert pat_local_url.match("https://127.0.0.1/")

    def test_case_insensitive(self):
        """Test pattern is case insensitive."""
        assert pat_local_url.match("HTTP://LOCALHOST:8000/")
        assert pat_local_url.match("http://LOCALHOST:8000/")

    def test_captures_host_and_port(self):
        """Test pattern captures host and port."""
        match = pat_local_url.match("http://localhost:8000/my/path")
        assert match is not None
        # The regex captures the scheme, host, and optional port
        full_match = match.group(0)
        assert "localhost" in full_match
        assert "8000" in full_match

    def test_search_finds_url_in_text(self):
        """Test pattern can find URL within larger text."""
        text = "Visit http://localhost:8000 for the app"
        match = pat_local_url.search(text)
        assert match is not None
        assert "localhost" in match.group(0)


class TestProxyUrlFilter:
    """Tests for ProxyUrlFilter logging filter."""

    def test_filter_creates_instance(self):
        """Test ProxyUrlFilter can be instantiated."""
        filter_obj = ProxyUrlFilter()
        assert filter_obj is not None

    def test_filter_returns_1(self):
        """Test filter always returns 1 (allow log record)."""
        filter_obj = ProxyUrlFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="http://localhost:8000/app",
            args=(),
            exc_info=None,
        )
        result = filter_obj.filter(record)
        assert result == 1

    def test_filter_transforms_url_in_proxy_env(self):
        """Test filter transforms URLs in proxy environment."""
        env = {
            "CODESPACES": "true",
            "CODESPACE_NAME": "myspace",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "preview.app.github.dev",
        }
        with patch.dict(os.environ, env, clear=True):
            filter_obj = ProxyUrlFilter()
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Visit http://localhost:8000/app",
                args=(),
                exc_info=None,
            )
            filter_obj.filter(record)
            assert "myspace-8000" in record.msg
            assert "localhost" not in record.msg

    def test_filter_handles_color_message(self):
        """Test filter handles color_message attribute."""
        env = {
            "CODESPACES": "true",
            "CODESPACE_NAME": "myspace",
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "preview.app.github.dev",
        }
        with patch.dict(os.environ, env, clear=True):
            filter_obj = ProxyUrlFilter()
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Visit http://localhost:8000/app",
                args=(),
                exc_info=None,
            )
            record.color_message = "Visit http://localhost:8000/app"  # type: ignore
            filter_obj.filter(record)
            assert "myspace-8000" in str(record.color_message)  # type: ignore


class TestPortCache:
    """Tests for port_cache module variable."""

    def test_port_cache_is_dict(self):
        """Test port_cache is a dictionary."""
        assert isinstance(port_cache, dict)
