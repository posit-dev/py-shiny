import pytest

from shiny._deprecated import ShinyDeprecationWarning
from shiny.ui import div, layout_column_wrap

X = div("42")
Y = div("43")
w = 1 / 2


def test_layout_column_width_as_first_param_is_deprecated():
    layout_column_wrap(X)
    with pytest.warns(ShinyDeprecationWarning, match="`width` parameter must be named"):
        layout_column_wrap(w, X)
    layout_column_wrap(X, w, Y)
    layout_column_wrap(X, Y, w)
    layout_column_wrap(X, Y, width=w)
    layout_column_wrap(X, Y, width=None)
