from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable, Optional
from unittest.mock import MagicMock

import pandas as pd
import pytest
from htmltools import tags

from shiny._namespaces import ResolvedId, Root
from shiny.render._render import (
    code,
    download,
    image,
    plot,
    table,
    text,
    ui as render_ui,
)
from shiny.render._try_render_plot import PlotSizeInfo
from shiny.session import session_context
from shiny.session._session import DownloadInfo
from shiny.types import ImgData


class _FakeSession:
    ns = Root
    id = "test_session"

    def __init__(self) -> None:
        self._downloads: dict[str, DownloadInfo] = {}
        self.output = MagicMock()

    def is_stub_session(self) -> bool:
        return False


class _StubSession:
    ns = Root
    id = "stub"

    def __init__(self) -> None:
        self._downloads: dict[str, DownloadInfo] = {}
        self.output = MagicMock()

    def is_stub_session(self) -> bool:
        return True


class _Input:
    def __init__(self, value: float) -> None:
        self._value = value

    def __call__(self) -> float:
        return self._value


class _PlotSession:
    ns = Root
    output = MagicMock()

    def __init__(
        self, output_id: str, *, pixelratio: float = 1.0, include_size: bool = False
    ):
        self.input = {Root(".clientdata_pixelratio"): _Input(pixelratio)}
        if include_size:
            self.input[Root(f".clientdata_output_{output_id}_width")] = _Input(300.0)
            self.input[Root(f".clientdata_output_{output_id}_height")] = _Input(400.0)

    def root_scope(self) -> "_PlotSession":
        return self


def _text_value() -> str:
    return "hello"


def _code_value() -> str:
    return "hello"


def _plot_value() -> None:
    return None


def test_text_auto_output_ui_inline_override():
    renderer = text(_text_value, inline=True)
    tag = renderer.auto_output_ui(inline=False)
    assert tag.attrs.get("class") == "shiny-text-output"
    assert tag.attrs.get("id") == "_text_value"
    assert tag.name == "div"


def test_text_auto_output_ui_default_inline():
    renderer = text(_text_value)
    tag = renderer.auto_output_ui()
    assert tag.name == "div"


def test_text_auto_output_ui_inline_true():
    renderer = text(_text_value)
    tag = renderer.auto_output_ui(inline=True)
    assert tag.name == "span"


def test_code_auto_output_ui_placeholder_default():
    renderer = code(_code_value, placeholder=False)
    tag = renderer.auto_output_ui()
    assert "noplaceholder" in tag.attrs.get("class", "")


def test_code_auto_output_ui_placeholder_override():
    renderer = code(_code_value)
    tag = renderer.auto_output_ui(placeholder=False)
    assert "noplaceholder" in tag.attrs.get("class", "")


def test_image_auto_output_ui_returns_output_image():
    renderer = image(lambda: {"src": "file.png"})
    renderer.output_id = "img"
    tag = renderer.auto_output_ui()
    assert tag.attrs.get("id") == "img"


def test_table_auto_output_ui_returns_output_table():
    renderer = table(lambda: pd.DataFrame({"a": [1]}))
    renderer.output_id = "tbl"
    tag = renderer.auto_output_ui()
    assert tag.attrs.get("id") == "tbl"


def test_render_ui_auto_output_ui_returns_output_ui():
    renderer = render_ui(lambda: tags.div("ok"))
    renderer.output_id = "ui"
    tag = renderer.auto_output_ui()
    assert tag.attrs.get("id") == "ui"


def test_download_auto_output_ui_returns_button():
    renderer = download(lambda: [b"data"])
    renderer.output_id = "download"
    tag = renderer.auto_output_ui()
    assert tag.name == "a"


@pytest.mark.asyncio
async def test_text_transform():
    renderer = text(lambda: "hello")
    assert await renderer.transform("hello") == "hello"


@pytest.mark.asyncio
async def test_code_transform():
    renderer = code(lambda: "hello")
    assert await renderer.transform("hello") == "hello"


@pytest.mark.asyncio
async def test_plot_returns_none_when_value_none_and_no_renderers(monkeypatch):
    sys_modules = __import__("sys").modules
    monkeypatch.delitem(sys_modules, "plotnine", raising=False)
    monkeypatch.delitem(sys_modules, "matplotlib", raising=False)
    monkeypatch.delitem(sys_modules, "PIL", raising=False)

    renderer = plot(lambda: None)
    renderer.output_id = "plot"
    session = _PlotSession("plot")
    with session_context(session):
        assert await renderer.render() is None


@pytest.mark.asyncio
async def test_plot_raises_on_unsupported_type(monkeypatch):
    sys_modules = __import__("sys").modules
    monkeypatch.delitem(sys_modules, "plotnine", raising=False)
    monkeypatch.delitem(sys_modules, "matplotlib", raising=False)
    monkeypatch.delitem(sys_modules, "PIL", raising=False)

    renderer = plot(lambda: object())
    renderer.output_id = "plot"
    session = _PlotSession("plot")
    with session_context(session):
        with pytest.raises(Exception, match="doesn't know to render objects"):
            await renderer.render()


@pytest.mark.asyncio
async def test_plot_uses_matplotlib_when_available(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "matplotlib", SimpleNamespace())

    def fake_render_matplotlib(*args: Any, **kwargs: Any):
        return True, {"src": "data:image/png;base64,aaa", "width": "100%"}

    monkeypatch.setattr(
        "shiny.render._render.try_render_matplotlib", fake_render_matplotlib
    )

    renderer = plot(lambda: object())
    renderer.output_id = "plot"
    session = _PlotSession("plot")
    with session_context(session):
        result = await renderer.render()
    assert isinstance(result, dict)
    assert result["src"].startswith("data:image/png;base64")


@pytest.mark.asyncio
async def test_plot_uses_plotnine_first(monkeypatch):
    calls: list[str] = []

    monkeypatch.setitem(__import__("sys").modules, "plotnine", SimpleNamespace())
    monkeypatch.setitem(__import__("sys").modules, "matplotlib", SimpleNamespace())

    def fake_render_plotnine(*args: Any, **kwargs: Any):
        calls.append("plotnine")
        return True, {"src": "data:image/png;base64,aaa", "width": "100%"}

    def fake_render_matplotlib(*args: Any, **kwargs: Any):
        calls.append("matplotlib")
        return True, {"src": "data:image/png;base64,bbb", "width": "100%"}

    monkeypatch.setattr(
        "shiny.render._render.try_render_plotnine", fake_render_plotnine
    )
    monkeypatch.setattr(
        "shiny.render._render.try_render_matplotlib", fake_render_matplotlib
    )

    renderer = plot(lambda: object())
    renderer.output_id = "plot"
    session = _PlotSession("plot")
    with session_context(session):
        result = await renderer.render()
    assert result["src"].endswith("aaa")
    assert calls == ["plotnine"]


@pytest.mark.asyncio
async def test_plot_uses_pil_when_available(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "PIL", SimpleNamespace())

    def fake_render_pil(*args: Any, **kwargs: Any):
        return True, {"src": "data:image/png;base64,ccc", "width": "100%"}

    monkeypatch.setattr("shiny.render._render.try_render_pil", fake_render_pil)

    renderer = plot(lambda: object())
    renderer.output_id = "plot"
    session = _PlotSession("plot")
    with session_context(session):
        result = await renderer.render()
    assert result["src"].endswith("ccc")


@pytest.mark.asyncio
async def test_plot_plotnine_false_falls_back_to_matplotlib(monkeypatch):
    sys_modules = __import__("sys").modules
    monkeypatch.setitem(sys_modules, "plotnine", SimpleNamespace())
    monkeypatch.setitem(sys_modules, "matplotlib", SimpleNamespace())

    def fake_render_plotnine(*args: Any, **kwargs: Any):
        return False, None

    def fake_render_matplotlib(*args: Any, **kwargs: Any):
        return True, {"src": "data:image/png;base64,aaa", "width": "100%"}

    monkeypatch.setattr(
        "shiny.render._render.try_render_plotnine", fake_render_plotnine
    )
    monkeypatch.setattr(
        "shiny.render._render.try_render_matplotlib", fake_render_matplotlib
    )

    renderer = plot(lambda: object())
    renderer.output_id = "plot"
    session = _PlotSession("plot")
    with session_context(session):
        result = await renderer.render()
    assert result["src"].endswith("aaa")


@pytest.mark.asyncio
async def test_plot_matplotlib_false_falls_back_to_pil(monkeypatch):
    sys_modules = __import__("sys").modules
    monkeypatch.delitem(sys_modules, "plotnine", raising=False)
    monkeypatch.setitem(sys_modules, "matplotlib", SimpleNamespace())
    monkeypatch.setitem(sys_modules, "PIL", SimpleNamespace())

    def fake_render_matplotlib(*args: Any, **kwargs: Any):
        return False, None

    def fake_render_pil(*args: Any, **kwargs: Any):
        return True, {"src": "data:image/png;base64,bbb", "width": "100%"}

    monkeypatch.setattr(
        "shiny.render._render.try_render_matplotlib", fake_render_matplotlib
    )
    monkeypatch.setattr("shiny.render._render.try_render_pil", fake_render_pil)

    renderer = plot(lambda: object())
    renderer.output_id = "plot"
    session = _PlotSession("plot")
    with session_context(session):
        result = await renderer.render()
    assert result["src"].endswith("bbb")


@pytest.mark.asyncio
async def test_plot_pil_false_allows_none(monkeypatch):
    sys_modules = __import__("sys").modules
    monkeypatch.delitem(sys_modules, "plotnine", raising=False)
    monkeypatch.delitem(sys_modules, "matplotlib", raising=False)
    monkeypatch.setitem(sys_modules, "PIL", SimpleNamespace())

    def fake_render_pil(*args: Any, **kwargs: Any):
        return False, None

    monkeypatch.setattr("shiny.render._render.try_render_pil", fake_render_pil)

    renderer = plot(lambda: None)
    renderer.output_id = "plot"
    session = _PlotSession("plot")
    with session_context(session):
        assert await renderer.render() is None


@pytest.mark.asyncio
async def test_image_transform_encodes_and_keeps_file(tmp_path: Path):
    img_path = tmp_path / "example.png"
    img_path.write_bytes(b"\x89PNG\r\n\x1a\n")

    renderer = image(lambda: {"src": str(img_path)})
    value: ImgData = {"src": str(img_path)}
    result = await renderer.transform(value)
    assert result is not None
    assert result["src"].startswith("data:image/png;base64,")
    assert img_path.exists()


@pytest.mark.asyncio
async def test_image_transform_deletes_file(tmp_path: Path):
    img_path = tmp_path / "example.jpg"
    img_path.write_bytes(b"\xff\xd8\xff")

    renderer = image(lambda: {"src": str(img_path)}, delete_file=True)
    value: ImgData = {"src": str(img_path)}
    await renderer.transform(value)
    assert not img_path.exists()


@pytest.mark.asyncio
async def test_image_transform_missing_file_raises(tmp_path: Path):
    missing_path = tmp_path / "missing.png"
    renderer = image(lambda: {"src": str(missing_path)})
    with pytest.raises(FileNotFoundError):
        await renderer.transform({"src": str(missing_path)})


@pytest.mark.asyncio
async def test_table_transform_dataframe():
    df = pd.DataFrame({"a": [1, 2]})
    renderer = table(lambda: df, index=True, classes="custom", border=1)
    result = await renderer.transform(df)
    assert "custom" in result["html"]
    assert "table" in result["html"]


@pytest.mark.asyncio
async def test_table_transform_styler():
    df = pd.DataFrame({"a": [1, 2]})
    styler = df.style
    renderer = table(lambda: styler)
    result = await renderer.transform(styler)
    assert "<table" in result["html"]


@pytest.mark.asyncio
async def test_table_transform_uses_as_data_frame(monkeypatch):
    class _Obj:
        pass

    class _Wrapped:
        def to_pandas(self) -> pd.DataFrame:
            return pd.DataFrame({"a": [1]})

    def fake_as_data_frame(value: Any):
        return _Wrapped()

    monkeypatch.setattr("shiny.render._render.as_data_frame", fake_as_data_frame)
    renderer = table(lambda: _Obj())
    result = await renderer.transform(_Obj())
    assert "<table" in result["html"]


@pytest.mark.asyncio
async def test_table_transform_type_error(monkeypatch):
    class _Obj:
        pass

    def fake_as_data_frame(value: Any):
        raise ValueError("nope")

    monkeypatch.setattr("shiny.render._render.as_data_frame", fake_as_data_frame)
    renderer = table(lambda: _Obj())
    with pytest.raises(TypeError, match="doesn't know how to render"):
        await renderer.transform(_Obj())


@pytest.mark.asyncio
async def test_render_ui_uses_session_process_ui():
    fake_session = MagicMock()
    fake_session.ns = ResolvedId("")
    fake_session._process_ui.return_value = {"deps": [], "html": "<div>ok</div>"}

    with session_context(fake_session):
        renderer = render_ui(lambda: tags.div("ok"))
        result = await renderer.transform(tags.div("ok"))

    assert result["html"] == "<div>ok</div>"
    fake_session._process_ui.assert_called_once()


@pytest.mark.asyncio
async def test_download_registers_handler_with_session():
    session = _FakeSession()

    def handler() -> Iterable[bytes]:
        yield b"abc"

    with session_context(session):
        decorator = download(filename="data.csv", media_type="text/csv")

        @decorator
        def file_handler():
            return handler()

    assert "file_handler" in session._downloads
    info = session._downloads["file_handler"]
    assert info.filename == "data.csv"
    assert info.content_type == "text/csv"


def test_download_does_not_register_with_stub_session():
    session = _StubSession()

    def handler() -> Iterable[bytes]:
        yield b"abc"

    with session_context(session):
        decorator = download(filename="data.csv", media_type="text/csv")

        @decorator
        def file_handler():
            return handler()

    assert session._downloads == {}


@pytest.mark.asyncio
async def test_download_url_quoting():
    session = _FakeSession()
    session.id = "session id"
    session.ns = ResolvedId("ns")

    with session_context(session):
        decorator = download(filename="data.csv")

        @decorator
        def file_handler():
            return [b"abc"]

        renderer = file_handler
        url = await renderer.render()
        assert "session%20id" in url
        assert "ns-file_handler" in url


def test_plot_size_info_explicit_zero_uses_native_size():
    size_info = PlotSizeInfo(
        container_size_px_fn=(lambda: 100.0, lambda: 200.0),
        user_specified_size_px=(0.0, None),
        pixelratio=1.0,
    )
    width, height, width_attr, height_attr = size_info.get_img_size_px(
        (1.0, 2.0), (2.0, 3.0), 72.0
    )
    assert width == 144.0
    assert width_attr == "144.0px"
    assert height == 200.0
    assert height_attr == "100%"


def test_plot_size_info_uses_container_when_missing():
    size_info = PlotSizeInfo(
        container_size_px_fn=(lambda: 111.0, lambda: 222.0),
        user_specified_size_px=(None, None),
        pixelratio=1.0,
    )
    width, height, width_attr, height_attr = size_info.get_img_size_px(
        (1.0, 2.0), (1.0, 2.0), 72.0
    )
    assert width == 111.0
    assert width_attr == "100%"
    assert height == 222.0
    assert height_attr == "100%"


def test_plot_size_info_explicit_sizes():
    size_info = PlotSizeInfo(
        container_size_px_fn=(lambda: 10.0, lambda: 20.0),
        user_specified_size_px=(300.0, 400.0),
        pixelratio=1.0,
    )
    width, height, width_attr, height_attr = size_info.get_img_size_px(
        (1.0, 2.0), (1.0, 2.0), 72.0
    )
    assert width == 300.0
    assert width_attr == "300.0px"
    assert height == 400.0
    assert height_attr == "400.0px"


def test_plot_auto_output_ui_sets_dimensions():
    renderer = plot(_plot_value, width=123, height=456)
    tag = renderer.auto_output_ui()
    assert tag.attrs.get("id") == "_plot_value"
    assert tag.attrs.get("style")


@pytest.mark.asyncio
async def test_plot_render_returns_none_when_renderer_returns_none(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "plotnine", SimpleNamespace())

    def fake_render_plotnine(*args: Any, **kwargs: Any):
        return True, None

    monkeypatch.setattr(
        "shiny.render._render.try_render_plotnine", fake_render_plotnine
    )

    session = _PlotSession("plot")
    with session_context(session):
        renderer = plot(lambda: object())
        renderer.output_id = "plot"
        result = await renderer.render()

    assert result is None


@pytest.mark.asyncio
async def test_plot_render_uses_container_size(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "matplotlib", SimpleNamespace())

    captured: dict[str, PlotSizeInfo] = {}

    def fake_render_matplotlib(
        x: object,
        *,
        plot_size_info: PlotSizeInfo,
        allow_global: bool,
        alt: Optional[str],
        **kwargs: object,
    ):
        captured["info"] = plot_size_info
        plot_size_info.get_img_size_px((1.0, 2.0), (1.0, 2.0), 72.0)
        return True, {"src": "data:image/png;base64,zzz", "width": "100%"}

    monkeypatch.setattr(
        "shiny.render._render.try_render_matplotlib", fake_render_matplotlib
    )

    session = _PlotSession("none", pixelratio=2.0, include_size=True)
    with session_context(session):
        renderer = plot(lambda: object())
        renderer.output_id = "none"
        await renderer.render()

    plot_size_info = captured["info"]
    assert plot_size_info.user_specified_size_px == (None, None)
    assert plot_size_info.pixelratio == 2.0
