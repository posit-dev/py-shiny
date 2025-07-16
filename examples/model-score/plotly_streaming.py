import functools
import json

import plotly.graph_objects as go
from shinywidgets import render_widget

from shiny import reactive


# Return a hash of an arbitrary object, including nested dicts, lists, and numpy/pandas
# data structures. Uses json.dumps() internally.
def _hash_anything(obj):
    return hash(json.dumps(obj, sort_keys=True, default=_to_json_repr))


def _to_json_repr(obj):
    # If has to_json(), use that; make sure it's callable
    if hasattr(obj, "to_json") and callable(obj.to_json):
        return json.loads(obj.to_json())
    if hasattr(obj, "to_list") and callable(obj.to_list):
        return obj.to_list()
    if hasattr(obj, "tolist") and callable(obj.tolist):
        return obj.tolist()
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def render_plotly_streaming(
    fn=None, *, recreate_key=lambda: None, update=("layout", "data")
):
    """Custom decorator for Plotly streaming plots. This is similar to
    shinywidgets.render_widget, except:

    1. You return simply a Figure, not FigureWidget.
    2. On reactive invalidation, the figure is updated in-place, rather than recreated
       from scratch.

    Parameters
    ----------
    recreate_key : callable, optional
        A function that returns a hashable object. If the value returned by this
        function changes, the plot will be recreated from scratch. This is useful for
        changes that render_plotly_streaming can't handle well, such as changing the
        number of traces in a plot.
    """

    if fn is not None:
        return render_plotly_streaming(recreate_key=recreate_key)(fn)

    def decorator(func):
        @deduplicate
        def recreate_trigger():
            return _hash_anything(recreate_key())

        @render_widget
        @functools.wraps(func)
        def wrapper():
            recreate_trigger()

            with reactive.isolate():
                fig = func()
                widget = go.FigureWidget(fig)

            @reactive.effect
            def update_plotly_data():
                f_new = func()
                with widget.batch_update():
                    if "layout" in update:
                        widget.update_layout(f_new.layout)
                    if "data" in update:
                        for old, new in zip(widget.data, f_new.data):
                            old.update(new)

            reactive.get_current_context().on_invalidate(update_plotly_data.destroy)

            return widget

        return wrapper

    return decorator


def deduplicate(func):
    with reactive.isolate():
        rv = reactive.value(func())

    @reactive.effect
    def update():
        x = func()
        with reactive.isolate():
            if x != rv():
                rv.set(x)

    @reactive.calc
    @functools.wraps(func)
    def wrapper():
        return rv()

    return wrapper
