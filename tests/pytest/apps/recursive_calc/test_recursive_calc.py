"""Regression test for recursive `reactive.calc` calls (see `Calc_` in
`shiny/reactive/_reactives.py`).
"""

from shiny.testserver import TestServerSession


def test_recursive_calc_returns_the_calling_frames_own_value(
    local_server: TestServerSession,
):
    local_server.set_inputs(n=5)
    assert local_server.get_output("result") == "5"

    local_server.set_inputs(n=3)
    assert local_server.get_output("result") == "3"

    local_server.set_inputs(n=1)
    assert local_server.get_output("result") == "1"
