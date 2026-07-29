from __future__ import annotations

import pytest

from shiny.run._run import (
    PORT_RANGE_DEFAULT,
    WORKER_PORT_RANGE_BASE,
    WORKER_PORT_RANGE_COUNT,
    WORKER_PORT_RANGE_SIZE,
    port_search_range,
)


def test_port_search_range_without_xdist(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    assert port_search_range() == PORT_RANGE_DEFAULT


def test_port_search_range_with_unparsable_worker_id(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "master")
    assert port_search_range() == PORT_RANGE_DEFAULT


@pytest.mark.parametrize("worker_num", [0, 1, 2, 7, 31])
def test_port_search_range_is_disjoint_per_worker(
    monkeypatch: pytest.MonkeyPatch, worker_num: int
):
    monkeypatch.setenv("PYTEST_XDIST_WORKER", f"gw{worker_num}")
    min_port, max_port = port_search_range()
    assert min_port == WORKER_PORT_RANGE_BASE + worker_num * WORKER_PORT_RANGE_SIZE
    assert max_port == min_port + WORKER_PORT_RANGE_SIZE - 1


def test_port_search_range_wraps_after_worker_cap(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw32")
    wrapped = port_search_range()
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw0")
    assert wrapped == port_search_range()


def test_worker_port_ranges_stay_within_valid_bounds(
    monkeypatch: pytest.MonkeyPatch,
):
    # Because worker numbers wrap at WORKER_PORT_RANGE_COUNT, checking
    # 0..WORKER_PORT_RANGE_COUNT-1 covers every range that can ever be produced.
    #
    # Every worker range must stay within random_port()'s default bounds
    # (PORT_RANGE_DEFAULT) and below 32768, where the Linux ephemeral port range
    # starts, so the OS never assigns one of our ports to an outgoing connection.
    for worker_num in range(WORKER_PORT_RANGE_COUNT):
        monkeypatch.setenv("PYTEST_XDIST_WORKER", f"gw{worker_num}")
        min_port, max_port = port_search_range()
        assert PORT_RANGE_DEFAULT[0] < min_port < max_port < 32768
        assert max_port < PORT_RANGE_DEFAULT[1]
