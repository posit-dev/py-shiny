from __future__ import annotations

import typing


def compare_annotations(
    ui_fn: typing.Callable[..., typing.Any], layout_fn: typing.Callable[..., typing.Any]
) -> None:
    ui_a = ui_fn.__annotations__
    layout_a = layout_fn.__annotations__
    keys: list[str] = []
    for key, _ in ui_a.items():
        keys.append(key)
    for key, _ in layout_a.items():
        if key not in keys:
            keys.append(key)
    for key in keys:
        if key == "args":
            assert key in ui_a
            assert key not in layout_a
        elif key == "return":
            ui_val = ui_a[key]
            layout_val = (
                layout_a[key].replace("RecallContextManager[", "").replace("]", "")
            )
            assert layout_val.endswith(ui_val)
        else:
            assert ui_a[key] == layout_a[key]
