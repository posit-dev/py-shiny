import pytest
from htmltools import Tag

from shiny._deprecated import ShinyDeprecationWarning
from shiny.ui import div, layout_column_wrap, layout_columns

X = div("42")
Y = div("43")
w = 1 / 2


def gap_spaced_wrappers(tag: Tag) -> list[Tag]:
    """The per-child wrappers added by `wrap_all_in_gap_spaced_container()`."""
    return [
        child
        for child in tag.children
        if isinstance(child, Tag)
        and "bslib-gap-spacing" in str(child.attrs.get("class", ""))
    ]


def test_layout_column_width_as_first_param_is_deprecated():
    layout_column_wrap(X)
    with pytest.warns(ShinyDeprecationWarning, match="`width` parameter must be named"):
        layout_column_wrap(w, X)
    layout_column_wrap(X, w, Y)
    layout_column_wrap(X, Y, w)
    layout_column_wrap(X, Y, width=w)
    layout_column_wrap(X, Y, width=None)


def test_layout_column_wrap_child_wrapper_class():
    wrappers = gap_spaced_wrappers(layout_column_wrap(X, Y))
    assert len(wrappers) == 2
    assert all(
        w.attrs["class"] == "bslib-gap-spacing html-fill-container" for w in wrappers
    )

    wrappers = gap_spaced_wrappers(layout_column_wrap(X, Y, fillable=False))
    assert [w.attrs["class"] for w in wrappers] == ["bslib-gap-spacing"] * 2


def test_layout_columns_child_wrapper_class():
    wrappers = gap_spaced_wrappers(layout_columns(X, Y))
    assert [w.attrs["class"] for w in wrappers] == [
        "bslib-gap-spacing bslib-grid-item html-fill-container"
    ] * 2


def test_child_wrappers_do_not_share_attrs():
    # The wrappers are built in a loop, so pin that each one owns its attributes:
    # editing one must not leak into its siblings. This holds today either way
    # (htmltools copies attrs into a fresh `TagAttrDict` per tag), so it does not
    # discriminate between implementations — it guards the invariant, so that
    # reintroducing a shared attrs dict fails here instead of silently emitting
    # wrong HTML if that htmltools behavior ever changes.
    wrappers = gap_spaced_wrappers(layout_column_wrap(X, Y, Y))
    assert len(wrappers) == 3

    wrappers[0].add_class("only-first")

    assert "only-first" in str(wrappers[0].attrs["class"])
    assert all("only-first" not in str(w.attrs["class"]) for w in wrappers[1:])
