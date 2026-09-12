"""Tests for the `local_server` fixture, which ships as part of shiny's pytest plugin."""

import pytest

from shiny.testserver import TestServerSession


def test_local_server_defaults_to_app_py_beside_the_test(
    local_server: TestServerSession,
):
    assert isinstance(local_server, TestServerSession)
    local_server.set_inputs(n=10)
    assert local_server.get_output("doubled") == "20"


@pytest.mark.parametrize("local_server", ["../local_server2/app.py"], indirect=True)
def test_local_server_takes_another_app_file_indirectly(
    local_server: TestServerSession,
):
    local_server.set_inputs(n=10)
    assert local_server.get_output("tripled") == "30"


def test_local_server_is_function_scoped(local_server: TestServerSession):
    # A fresh session each test: the `n` the first test set is gone, so tests
    # cannot affect each other through the inputs they leave behind.
    with pytest.raises(KeyError):
        local_server.get_input("n")
