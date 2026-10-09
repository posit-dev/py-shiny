"""Tests for the download renderers' handler registration and auto-placed UI."""

from __future__ import annotations

from typing import AsyncIterable, Callable

import pytest
from htmltools import Tag

from shiny import App, Inputs, Outputs, Session, module, render, ui
from shiny._connection import MockConnection
from shiny.express import output_args
from shiny.session import session_context


def _new_session() -> Session:
    return App(ui.TagList(), None)._create_session(MockConnection())


def test_download_registers_under_function_name():
    session = _new_session()

    with session_context(session):

        @render.download_button(filename="file.txt")
        async def my_download() -> AsyncIterable[str]:
            yield "hello"

    assert list(session._downloads.keys()) == ["my_download"]


def test_download_registers_under_output_id():
    """`@output(id=)` renames the download control; the handler must follow."""
    session = _new_session()

    with session_context(session):

        @session.output(id="download4")
        @render.download_button(filename="file.txt")
        async def _() -> AsyncIterable[str]:
            yield "hello"

    # Exact equality matters: the renderer auto-registers under the value function's
    # name (`_`) before `@output(id=)` re-registers it, so a lingering `_` key would
    # mean the download is also served under a name the app never declared.
    assert list(session._downloads.keys()) == ["download4"]


def test_download_registers_under_namespaced_output_id():
    session = _new_session()

    @module.server
    def mod_server(input: Inputs, output: Outputs, session: Session):
        @output(id="download4")
        @render.download_button(filename="file.txt")
        async def _() -> AsyncIterable[str]:
            yield "hello"

    with session_context(session):
        mod_server("mod1")

    # Downloads are always stored fully namespaced in the root session, and the
    # auto-registered `mod1-_` entry must not survive the rename.
    assert list(session._downloads.keys()) == ["mod1-download4"]


@pytest.mark.parametrize(
    "renderer, ui_fn",
    [
        (render.download_button, ui.download_button),
        (render.download_link, ui.download_link),
    ],
)
def test_download_auto_ui_takes_icon_and_attributes(
    renderer: type[render.download_button], ui_fn: Callable[..., Tag]
):
    icon = ui.tags.i(class_="fa-solid fa-download")

    @renderer(filename="report.txt", label="Report", icon=icon, class_="btn-success")
    async def report() -> AsyncIterable[str]:
        yield "hello"

    expected = ui_fn("report", "Report", icon=icon, class_="btn-success")
    assert str(report.tagify()) == str(expected)

    # `output_args()` overrides what the decorator was given
    other_icon = ui.tags.i(class_="fa-solid fa-file")

    @output_args(label="Get it", icon=other_icon, title="Get the report")
    @renderer(filename="report.txt", icon=icon)
    async def report2() -> AsyncIterable[str]:
        yield "hello"

    expected = ui_fn("report2", "Get it", icon=other_icon, title="Get the report")
    assert str(report2.tagify()) == str(expected)
