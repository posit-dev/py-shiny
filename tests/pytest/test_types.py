from __future__ import annotations

import copy

from shiny.types import DEPRECATED, MISSING, Jsonifiable


def test_missing_sentinels_survive_copying():
    # A sentinel is identified by identity, so a copy must be the same object --
    # `dataclasses.asdict`/`astuple` deep-copy their fields, and a copied
    # sentinel would stop comparing equal to `MISSING`.
    for sentinel in (MISSING, DEPRECATED):
        assert copy.copy(sentinel) is sentinel
        assert copy.deepcopy(sentinel) is sentinel
        assert copy.deepcopy({"a": [sentinel]})["a"][0] is sentinel


def test_missing_sentinels_repr_by_name():
    assert repr(MISSING) == "MISSING"
    assert repr(DEPRECATED) == "DEPRECATED"


def test_jsonifiable_accepts_concrete_containers():
    # Regression for #2497: `Jsonifiable` used invariant `List`/`Dict`, so a
    # `dict[str, int]` returned from a function was a pyright error. Pyright
    # checks the assignments below; the runtime assert just keeps them in use.
    def counts() -> dict[str, int]:
        return {"a": 1}

    def names() -> list[str]:
        return ["a"]

    def nested() -> dict[str, list[int]]:
        return {"a": [1]}

    values: list[Jsonifiable] = [counts(), names(), nested(), ("a", 1)]
    assert len(values) == 4
