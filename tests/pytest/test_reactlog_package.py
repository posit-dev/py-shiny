from pathlib import Path

import shiny.reactive


def test_reactive_package_does_not_import_reactlog() -> None:
    init = Path(shiny.reactive.__file__).read_text(encoding="utf-8")
    assert "_reactlog" not in init


def test_reactlog_package_exports() -> None:
    from shiny.reactive._reactlog import (
        ReactlogRecorder,
        format_graph_mermaid,
        format_reactlog_html,
        load_reactlog_json,
        session_picker_html,
    )

    assert all(
        callable(x)
        for x in (
            ReactlogRecorder,
            format_graph_mermaid,
            format_reactlog_html,
            load_reactlog_json,
            session_picker_html,
        )
    )
