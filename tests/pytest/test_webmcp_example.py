"""The WebMCP example's server contract, using the fixture from #2495."""

import json

import pytest

from shiny.testserver import TestServerSession

pytestmark = pytest.mark.parametrize(
    "local_server", ["../../examples/webmcp/app.py"], indirect=True
)


def test_sales_summary_and_request_correlation(local_server: TestServerSession):
    local_server.set_inputs(region="West", channel="Online", webmcp_request_id="one")
    assert json.loads(local_server.get_output("summary").value) == {
        "request_id": "one",
        "filters": {"region": "West", "channel": "Online"},
        "orders": 2,
        "revenue": 600,
        "average_order": 300,
        "currency": "USD",
    }
    local_server.set_inputs(channel="Retail", webmcp_request_id="two")
    result = json.loads(local_server.get_output("summary").value)
    assert result["request_id"] == "two"
    assert result["revenue"] == 300
    assert result["average_order"] == 150


def test_all_sales_and_repeated_reads(local_server: TestServerSession):
    local_server.set_inputs(region="All", channel="All", webmcp_request_id="one")
    result = json.loads(local_server.get_output("summary").value)
    assert result["orders"] == 8
    assert result["revenue"] == 1800
    local_server.set_inputs(webmcp_request_id="two")
    result["request_id"] = "two"
    assert json.loads(local_server.get_output("summary").value) == result


@pytest.mark.parametrize(
    "filters",
    [
        {"region": "Unknown", "channel": "Online"},
        {"region": "West", "channel": "Unknown"},
        {"region": None, "channel": "Online"},
    ],
)
def test_invalid_filters_are_recoverable(
    local_server: TestServerSession, filters: dict[str, str | None]
):
    local_server.set_inputs(**filters, webmcp_request_id="bad")
    result = json.loads(local_server.get_output("summary").value)
    assert result["request_id"] == "bad"
    assert "error" in result
    local_server.set_inputs(region="North", channel="Retail", webmcp_request_id="ok")
    result = json.loads(local_server.get_output("summary").value)
    assert result["revenue"] == 100
    assert "error" not in result
