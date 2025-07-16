from __future__ import annotations

import great_tables as gt

from shiny.render._data_frame_utils._styles import StyleInfo
from shiny.types import Jsonifiable


def gt_style_str_to_obj(style_str: str) -> dict[str, Jsonifiable]:
    # Could use BeautifulSoup here, but this is a simple example
    style_obj: dict[str, Jsonifiable] = {}
    for style_part in style_str.split(";"):
        style_part = style_part.strip()
        if not style_part:
            continue
        key, value = style_part.split(":")
        style_obj[key] = value.strip()
    return style_obj


def gt_styles(df_gt: gt.GT) -> list[StyleInfo]:
    styles = df_gt._styles
    ret: list[StyleInfo] = []
    for style in styles:
        location = style.locname
        location = (
            "body"
            if location == "data"  # pyright: ignore[reportUnnecessaryComparison]
            else location
        )
        assert location == "body", f"`style.locname` is {location}, expected 'body'"
        rows = style.rownum
        assert rows is not None
        cols = style.colnum
        if cols is None:
            cols = style.colname
        assert cols is not None

        style_obj: dict[str, Jsonifiable] = {}
        for style_str in style.styles:
            style_obj.update(
                gt_style_str_to_obj(style_str._to_html_style()),
            )
        ret.append(
            {
                "location": location,  # pyright: ignore[reportArgumentType]
                "rows": rows,
                "cols": cols,
                "style": style_obj,
            }
        )
    return ret
