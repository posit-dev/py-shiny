from ipywidgets.widgets import DOMWidget
from ipywidgets.embed import embed_data, dependency_state, embed_snippet
from htmltools import tags, Tag, TagList
from .html_dependencies import ipywidget_embed_dep
import json


def input_ipywidget(id: str, widget: DOMWidget) -> Tag:
    ui = _get_ipywidget_html(widget)
    return tags.div(ui, id=id, class_="shiny-ipywidget-input shiny-ipywidget")


def _get_ipywidget_html(widget: DOMWidget) -> TagList:
    dat = embed_data(views=widget, state=dependency_state(widget))
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
        # TODO: bake this logic into Shiny itself and remove this?
        ipywidget_embed_dep(),
    )
