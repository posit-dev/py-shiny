from __future__ import annotations

import pytest

from shiny.run._run import (
    PORT_RANGE_DEFAULT,
    WORKER_PORT_RANGE_BASE,
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


def test_port_search_range_stays_below_linux_ephemeral_ports(
    monkeypatch: pytest.MonkeyPatch,
):
    # The Linux ephemeral port range starts at 32768. Ports handed to Shiny apps
    # must stay below it so the OS never assigns one of our ports to an outgoing
    # connection.
    for worker_num in range(0, 64):
        monkeypatch.setenv("PYTEST_XDIST_WORKER", f"gw{worker_num}")
        min_port, max_port = port_search_range()
        assert 1024 < min_port < max_port < 32768
