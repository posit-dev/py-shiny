import functools

import plotly.graph_objects as go
from shinywidgets import render_widget

from shiny import reactive


def render_plotly_streaming(fn=None, *, recreate_when=lambda: None):
    """Custom decorator for Plotly streaming plots. This is similar to
    shinywidgets.render_widget, except:

    1. You return simply a Figure, not FigureWidget.
    2. On reactive invalidation, the figure is updated in-place, rather than recreated
       from scratch.
    """

    if fn is not None:
        return render_plotly_streaming(recreate_when=recreate_when)(fn)

    def decorator(func):
        @render_widget
        @functools.wraps(func)
        def wrapper():
            recreate_when()

            with reactive.isolate():
                fig = func()
                widget = go.FigureWidget(fig)

            @reactive.Effect
            def update_plotly_data():
                f_new = func()
                with widget.batch_update():
                    widget.update_layout(f_new.layout)
                    for old, new in zip(widget.data, f_new.data):
                        old.update(new)

            reactive.get_current_context().on_invalidate(update_plotly_data.destroy)

            return widget

        return wrapper

    return decorator
