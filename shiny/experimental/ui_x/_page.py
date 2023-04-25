from __future__ import annotations

from typing import Optional

from htmltools import TagAttrs, TagChild, css, tags

from shiny import ui

from ._css import CssUnit, validate_css_unit
from ._fill import bind_fill_role


def page_fillable(
    *args: TagChild | TagAttrs,
    padding: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    fill_mobile: bool = False,
    title: Optional[str] = None,
    lang: Optional[str] = None,
):
    style = css(
        # TODO: validate_css_padding(padding)
        padding=validate_css_unit(padding),
        gap=validate_css_unit(gap),
        __bslib_page_fill_mobile_height="100%" if fill_mobile else "auto",
    )

    return ui.page_bootstrap(
        tags.head(tags.style("html { height: 100%; }")),
        bind_fill_role(
            tags.body(class_="bslib-page-fill", style=style, *args),
            container=True,
        ),
        title=title,
        lang=lang,
    )
