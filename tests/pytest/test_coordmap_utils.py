"""Tests for shiny.render._coordmap helpers."""

from __future__ import annotations

import types
from typing import cast

import pytest

from shiny.render._coordmap import (
    _get_mappings,
    _is_log_trans,
    _is_reverse_trans,
    _simplify_type,
)
from shiny.types import PlotnineFigure


def test_is_log_trans_and_reverse() -> None:
    class log10_trans:  # noqa: N801
        pass

    class reverse_trans:  # noqa: N801
        pass

    assert _is_log_trans(log10_trans()) is True
    assert _is_log_trans(object()) is False
    assert _is_reverse_trans(reverse_trans()) is True
    assert _is_reverse_trans(object()) is False


def test_simplify_type_with_fake_numpy(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeInt(int):
        pass

    class FakeFloat(float):
        pass

    fake_numpy = types.SimpleNamespace(integer=FakeInt, floating=FakeFloat)
    monkeypatch.setitem(__import__("sys").modules, "numpy", fake_numpy)

    assert _simplify_type(FakeInt(5)) == 5
    assert _simplify_type(FakeFloat(1.5)) == 1.5
    assert _simplify_type("x") == "x"


def test_get_mappings_with_facets() -> None:
    class facet_grid:  # noqa: N801
        cols = ["cyl"]
        rows = ["gear"]

    class facet_wrap:  # noqa: N801
        vars = ["am"]

    class coord_flip:  # noqa: N801
        pass

    class FakeLayout:
        coord = coord_flip()
        facet = facet_grid()

    class FakePlot:
        mapping = {"x": "wt", "y": "mpg"}
        layout = FakeLayout()

    mapping = _get_mappings(cast(PlotnineFigure, FakePlot()))
    assert mapping["x"] == "mpg"
    assert mapping["y"] == "wt"
    assert mapping.get("panelvar1") == "cyl"
    assert mapping.get("panelvar2") == "gear"

    class FakeLayoutWrap:
        coord = object()
        facet = facet_wrap()

    class FakePlotWrap:
        mapping = {}
        layout = FakeLayoutWrap()

    mapping_wrap = _get_mappings(cast(PlotnineFigure, FakePlotWrap()))
    assert mapping_wrap.get("panelvar1") == "am"
