from pathlib import Path

import shiny.reactive
from shiny.reactive._reactlog import (
    ReactlogRecorder,
    session_picker_html,
)


def test_reactive_package_does_not_import_reactlog() -> None:
    init = Path(shiny.reactive.__file__).read_text(encoding="utf-8")
    assert "_reactlog" not in init


def test_reactlog_package_exports() -> None:
    assert all(
        callable(x)
        for x in (
            ReactlogRecorder,
            session_picker_html,
        )
    )
