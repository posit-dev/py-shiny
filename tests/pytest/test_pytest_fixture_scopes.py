"""
Lock down the scope of every pytest fixture shiny ships.

A scope is read off the registered fixture definition, not inferred from state
left behind by an earlier test, so these hold under xdist and any test order.
"""

from typing import cast

import pytest

from shiny.pytest import create_app_fixture

# `create_app_fixture()` returns a fixture; it registers by being a module attribute.
app_default_scope = create_app_fixture("apps/local_server1/app.py")
app_default_scope_list = create_app_fixture(
    ["apps/local_server1/app.py", "apps/local_server2/app.py"]
)
app_session_scope = create_app_fixture("apps/local_server1/app.py", scope="session")


def _fixture_scope(request: pytest.FixtureRequest, name: str) -> str:
    # pytest leaves `request.node` unannotated.
    node = cast(pytest.Item, request.node)  # pyright: ignore[reportUnknownMemberType]
    fixture_defs = (
        request._fixturemanager.getfixturedefs(  # pyright: ignore[reportPrivateUsage]
            name, node
        )
    )
    assert fixture_defs is not None, f"no fixture named {name!r}"
    (fixture_def,) = fixture_defs
    return fixture_def.scope


@pytest.mark.parametrize(
    "name, scope",
    [
        # Shipped by the `shiny-test` pytest plugin.
        ("local_app", "module"),
        # A session holds the inputs set so far; sharing one across tests would
        # let them affect each other.
        ("local_server", "function"),
        # Made with `create_app_fixture()`.
        ("app_default_scope", "module"),
        ("app_default_scope_list", "module"),
        ("app_session_scope", "session"),
    ],
)
def test_fixture_scope(request: pytest.FixtureRequest, name: str, scope: str):
    assert _fixture_scope(request, name) == scope
