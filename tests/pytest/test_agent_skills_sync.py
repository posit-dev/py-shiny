"""Guard that bundled Agent Skills stay in sync with the public APIs they document.

The bundled `shiny-for-python` skill (``shiny/.agents/skills/``) is user-facing
documentation, with one per-topic reference file under ``references/``, but
nothing at runtime fails if the code a reference describes is renamed or removed
-- the reference just silently goes stale. These tests assert that the API
surface a reference documents is still mentioned in its file, so renames and
removals fail loudly here. They check presence only, not prose accuracy.
"""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

import pytest

import shiny.otel
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny._connection import MockConnection
from shiny.otel._collect import OtelCollectLevel

REPO_ROOT = Path(__file__).parents[2]
REFERENCES_DIR = (
    REPO_ROOT / "shiny" / ".agents" / "skills" / "shiny-for-python" / "references"
)


def reference_text(topic: str) -> str:
    return (REFERENCES_DIR / f"{topic}.md").read_text()


def test_otel_reference_mentions_public_exports() -> None:
    text = reference_text("otel")
    for export in shiny.otel.__all__:
        assert f"otel.{export}" in text, (
            f"shiny.otel.__all__ export `{export}` is not mentioned in the otel "
            "reference -- update references/otel.md to match the public API."
        )


def test_otel_reference_mentions_collect_levels() -> None:
    text = reference_text("otel")
    assert "SHINY_OTEL_COLLECT" in text
    for level in OtelCollectLevel:
        assert f"`{level.name.lower()}`" in text, (
            f"OtelCollectLevel.{level.name} is not documented in the otel "
            "reference's collection-levels table."
        )


def test_shiny_doctor_references() -> None:
    doctor_dir = REPO_ROOT / "shiny" / ".agents" / "skills" / "shiny-doctor"
    skill_text = (doctor_dir / "SKILL.md").read_text()
    assert "shiny-doctor" in skill_text
    assert (doctor_dir / "references" / "antipatterns.md").is_file()
    assert (doctor_dir / "references" / "diagnostics-checklist.md").is_file()
    antipatterns_text = (doctor_dir / "references" / "antipatterns.md").read_text()
    assert "@reactive.calc" in antipatterns_text
    assert "@reactive.extended_task" in antipatterns_text
    assert "reactive.value" in antipatterns_text


def test_shiny_doctor_concurrency_and_module_accuracy() -> None:
    doctor_dir = REPO_ROOT / "shiny" / ".agents" / "skills" / "shiny-doctor"
    skill_text = (doctor_dir / "SKILL.md").read_text()
    antipatterns_text = (doctor_dir / "references" / "antipatterns.md").read_text()
    checklist_text = (
        doctor_dir / "references" / "diagnostics-checklist.md"
    ).read_text()

    assert "session.ns" not in skill_text
    assert "missing ns() wrapper" not in antipatterns_text
    assert "asyncio.to_thread" in antipatterns_text
    assert "ProcessPoolExecutor" in antipatterns_text
    assert "cannot directly read reactive sources" in skill_text
    assert '@output(id="summary_output")' in antipatterns_text
    assert "@output(id=" in skill_text
    assert "Runtime Verified" in skill_text
    assert "Server Startup Verified" in skill_text
    assert "managed background process" in skill_text
    assert "timeout" in skill_text
    assert "secrets" in checklist_text
    assert "Do not rely on `python app.py`" in skill_text
    assert "from shiny import input" not in antipatterns_text
    assert "initial_val = val()" in antipatterns_text
    assert "@reactive.event(input.add_btn)" in antipatterns_text
    assert "shiny.test" not in skill_text
    assert "shiny.pytest" in skill_text


def test_shiny_doctor_code_blocks_compile() -> None:
    doctor_dir = REPO_ROOT / "shiny" / ".agents" / "skills" / "shiny-doctor"
    for md_file in doctor_dir.rglob("*.md"):
        content = md_file.read_text()
        code_blocks = re.findall(r"```python\n(.*?)```", content, re.DOTALL)
        for i, code in enumerate(code_blocks):
            try:
                compile(code, f"{md_file.name}_block_{i}", "exec")
            except SyntaxError as e:
                raise AssertionError(
                    f"Syntax error in code block {i} in {md_file.name}: {e}\nCode:\n{code}"
                ) from e


def test_shiny_doctor_markdown_links() -> None:
    doctor_dir = REPO_ROOT / "shiny" / ".agents" / "skills" / "shiny-doctor"
    for md_file in doctor_dir.rglob("*.md"):
        content = md_file.read_text()
        links = re.findall(r"\[.*?\]\((references/[^\)]+)\)", content)
        for link in links:
            target_path = (doctor_dir / link.split("#")[0]).resolve()
            assert target_path.is_file(), f"Broken link {link} in {md_file.name}"


@pytest.mark.asyncio
async def test_shiny_doctor_output_id_override_runtime() -> None:
    def server(input: Inputs, output: Outputs, session: Session):
        @output(id="summary_output")
        @render.text
        def make_summary():
            return "Done"

    conn = MockConnection()
    app = App(ui.TagList(), server)
    sess = app._create_session(conn)

    async def mock_client():
        conn.cause_receive('{"method":"init","data":{}}')
        conn.cause_disconnect()

    await asyncio.gather(mock_client(), sess._run())
    assert "summary_output" in sess.output._outputs
    assert "make_summary" not in sess.output._outputs


@pytest.mark.asyncio
async def test_shiny_doctor_extended_task_semantics_runtime() -> None:
    def blocking_work(val: str) -> str:
        return f"result_{val}"

    @reactive.extended_task
    async def task_with_param(val: str) -> str:
        return await asyncio.to_thread(blocking_work, val)

    task_with_param("input_val")
    await asyncio.sleep(0.05)

    with reactive.isolate():
        assert task_with_param.result() == "result_input_val"

    val_src = reactive.value("bad_read")

    @reactive.extended_task
    async def task_with_reactive_read():
        return val_src()

    task_with_reactive_read()
    await asyncio.sleep(0.05)

    with reactive.isolate():
        with pytest.raises(RuntimeError, match=r"not allowed to read reactive sources"):
            task_with_reactive_read.result()
