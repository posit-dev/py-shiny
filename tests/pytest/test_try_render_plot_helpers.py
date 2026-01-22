"""Tests for shiny.render._try_render_plot helpers."""

from __future__ import annotations

# pyright: reportUnknownMemberType=false

import sys
import types
from typing import TYPE_CHECKING, Any, cast

import pytest

from shiny.render import _try_render_plot
from shiny.render._try_render_plot import (
    PlotSizeInfo,
    cast_to_size_tuple,
    get_desired_dpi_from_fig,
    get_matplotlib_figure,
    try_render_matplotlib,
    try_render_pil,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def test_plot_size_info_user_specified_zero() -> None:
    calls = {"w": 0, "h": 0}

    def width() -> float:
        calls["w"] += 1
        return 111.0

    def height() -> float:
        calls["h"] += 1
        return 222.0

    info = PlotSizeInfo((width, height), (0, 0), pixelratio=2)
    width_px, height_px, width_attr, height_attr = info.get_img_size_px(
        (4, 5), (6, 7), dpi=10
    )

    assert width_px == 60
    assert height_px == 70
    assert width_attr == "60px"
    assert height_attr == "70px"
    assert calls == {"w": 0, "h": 0}


def test_plot_size_info_container_size() -> None:
    info = PlotSizeInfo((lambda: 120.0, lambda: 90.0), (None, None), pixelratio=1)
    width_px, height_px, width_attr, height_attr = info.get_img_size_px(
        (1, 1), (1, 1), dpi=100
    )
    assert width_px == 120.0
    assert height_px == 90.0
    assert width_attr == "100%"
    assert height_attr == "100%"


def test_cast_to_size_tuple() -> None:
    assert cast_to_size_tuple([1, 2]) == (1, 2)


def test_get_desired_dpi_from_fig_uses_original() -> None:
    class DummyCanvas:
        device_pixel_ratio = 2

    class DummyFig:
        canvas = DummyCanvas()
        _original_dpi = 50

        def get_dpi(self) -> float:
            return 100

    assert get_desired_dpi_from_fig(cast("Figure", DummyFig())) == 50


def test_get_matplotlib_figure_global_not_allowed() -> None:
    import matplotlib.pyplot as plt

    plt.figure()
    with pytest.raises(RuntimeError, match="cannot be used from an async render"):
        get_matplotlib_figure(None, allow_global=False)

    assert plt.get_fignums() == []


def test_get_matplotlib_figure_from_artist_and_list() -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    line = ax.plot([1, 2], [3, 4])[0]

    assert get_matplotlib_figure(line, allow_global=True) is fig
    assert get_matplotlib_figure([line], allow_global=True) is fig

    plt.close(fig)


def test_try_render_matplotlib_basic(monkeypatch: pytest.MonkeyPatch) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([0, 1], [1, 0])

    def fake_get_coordmap(_fig: object) -> dict[str, bool]:
        return {"ok": True}

    monkeypatch.setattr(_try_render_plot, "get_coordmap", fake_get_coordmap)

    info = PlotSizeInfo((lambda: 200.0, lambda: 150.0), (None, None), pixelratio=1)
    ok, res = try_render_matplotlib(
        fig,
        plot_size_info=info,
        allow_global=False,
        alt="Alt text",
    )

    assert ok is True
    assert res is not None
    assert res["src"].startswith("data:image/png;base64,")
    assert res.get("width") == "100%"
    assert res.get("height") == "100%"
    assert res.get("alt") == "Alt text"
    assert res.get("coordmap") == {"ok": True}


def test_try_render_pil_with_fake_module(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_pil = types.ModuleType("PIL")
    fake_pil_image = types.ModuleType("PIL.Image")

    class FakeImage:
        def save(self, buf: Any, format: str = "PNG", **kwargs: object) -> None:
            buf.write(b"fake")

    fake_pil_image.__dict__["Image"] = FakeImage
    fake_pil.__dict__["Image"] = fake_pil_image

    monkeypatch.setitem(sys.modules, "PIL", fake_pil)
    monkeypatch.setitem(sys.modules, "PIL.Image", fake_pil_image)

    image = FakeImage()
    info = PlotSizeInfo((lambda: 10.0, lambda: 20.0), (None, None), pixelratio=1)
    ok, res = try_render_pil(image, plot_size_info=info, alt="Alt")

    assert ok is True
    assert res is not None
    assert res["src"].startswith("data:image/png;base64,")
    assert res.get("width") == "100%"
    assert res.get("height") == "100%"
    assert res.get("style") == "object-fit:contain"
    assert res.get("alt") == "Alt"
