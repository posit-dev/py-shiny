from ipywidgets.widgets import DOMWidget
from ipywidgets.embed import embed_data, dependency_state
from htmltools import tags, Tag, TagList
from .html_dependencies import ipywidget_embed_deps, ipywidget_input_dep
import json
from typing import Dict, Any


def input_ipywidget(id: str, widget: object) -> Tag:
    if not isinstance(widget, DOMWidget):
        raise TypeError("widget must be a DOMWidget")
    if not hasattr(widget, "value"):
        raise RuntimeError(
            "widget must have a value property to be treated as an input. "
            + "Do you want to render this widget as an output (i.e., output_ipywidget())?"
        )
    return tags.div(
        _get_ipywidget_html(widget),
        ipywidget_embed_deps(),
        ipywidget_input_dep(),
        id=id,
        class_="shiny-ipywidget-input",
    )


# TODO:
# 1. allow a way to customize the CDN
# 2. Do setattr(ipy.DOMWidget, 'tagify', _get_ipywidget_html) so we can statically render ipywidgets in py-htmltools
def _get_ipywidget_html(widget: DOMWidget) -> TagList:
    dat: Dict[str, Any] = embed_data(
        views=[widget], state=dependency_state(widgets=[widget])
    )
    return TagList(
        tags.script(
            json.dumps(dat["manager_state"]),
            type="application/vnd.jupyter.widget-state+json",
            data_jupyter_widgets_cdn_only="",
        ),
        tags.script(
            [json.dumps(view) for view in dat["view_specs"]],
            type="application/vnd.jupyter.widget-view+json",
            data_jupyter_widgets_cdn_only="",
        ),
    )
