from pathlib import Path

from shiny.bookmark._restore_state import RestoreState
from shiny.module import ResolvedId


def test_state_within_namespace_dir_matches_save_dir():
    # `BookmarkProxy._scoped_on_bookmark()` saves module files to `dir / ns`
    ns = ResolvedId("outer")("inner")
    state = RestoreState(
        input={"outer-inner-x": 1, "other-x": 2}, values={}, dir=Path("/root")
    )

    scoped = state._state_within_namespace(ns)

    assert scoped.dir == Path("/root") / ns
    assert scoped.input == {"x": 1}
