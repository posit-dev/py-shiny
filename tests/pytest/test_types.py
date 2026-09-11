from __future__ import annotations

import copy

from shiny.types import DEPRECATED, MISSING


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
