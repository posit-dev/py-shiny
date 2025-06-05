import os
import warnings

import pytest

from shiny._main import _set_workbench_kwargs


def test_workbench_kwargs_if_url_set():
    """
    Test that the `ws_per_message_deflate` kwarg is set to False when
    RS_SERVER_URL and RS_SESSION_URL are set in the environment.
    This is to avoid breaking issues in Workbench.
    If the kwargs are set to True, a warning is raised and the value is set to False.
    """
    # Workbench URL is set, kwargs are not
    os.environ["RS_SERVER_URL"] = "any_string"
    os.environ["RS_SESSION_URL"] = "any_string"

    kwargs = {}
    _set_workbench_kwargs(kwargs)
    assert kwargs.get("ws_per_message_deflate") is False

    # kwarg have been set to True
    kwargs = {
        "ws_per_message_deflate": True,
    }
    with pytest.warns(UserWarning):
        warnings.warn(
            "Overwriting kwarg `ws_per_message_deflate=True` to `False` to avoid breaking issue in Workbench",
            UserWarning,
        )
        _set_workbench_kwargs(kwargs)
        assert kwargs.get("ws_per_message_deflate") is False

    # Teardown
    del os.environ["RS_SERVER_URL"]
    del os.environ["RS_SESSION_URL"]


def test_workbench_kwargs_if_url_not_set():
    """
    Test that the `ws_per_message_deflate` kwarg is not changed if the RS_SERVER_URL and RS_SESSION_URL environment variables are not set are set.
    """
    kwargs = {
        "ws_per_message_deflate": True,
    }
    _set_workbench_kwargs(kwargs)
    assert kwargs.get("ws_per_message_deflate") is True

    kwargs = {}
    _set_workbench_kwargs(kwargs)
    assert kwargs.get("ws_per_message_deflate") is None
