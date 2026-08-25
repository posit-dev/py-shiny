from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page, expect

from shiny._inspect import (
    format_reactlog_html,
    generate_reactlog,
    record_shiny_session,
)


def test_graph_elements_visible_on_initialization(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("x", "X", 1)
ui.input_numeric("y", "Y", 2)

@reactive.calc
def doubled():
    return input.x() * 2

@render.text
def result():
    return str(doubled())

@render.text
def other():
    return str(input.y())
"""
    reactlog = generate_reactlog(code, inputs={"x": 1, "y": 2})
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    nodes = page.locator(".graph-node")
    assert nodes.count() == 5

    edges = page.locator(".graph-edge")
    assert edges.count() == 3

    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('.graph-edge')).every(edge => parseFloat(window.getComputedStyle(edge).opacity) > 0.5)"
    )


def test_hover_highlights_connections(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("x", "X", 1)
ui.input_numeric("y", "Y", 2)

@reactive.calc
def doubled():
    return input.x() * 2

@render.text
def result():
    return str(doubled())

@render.text
def other():
    return str(input.y())
"""
    reactlog = generate_reactlog(code, inputs={"x": 1, "y": 2})
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    page.locator('.graph-node[data-id="calc:doubled"]').hover()
    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('.graph-edge')).some(edge => parseFloat(edge.style.opacity) === 1)"
    )

    page.locator(".toolbar").hover()
    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('.graph-edge')).every(edge => parseFloat(edge.style.opacity) >= 0.6)"
    )


def test_app_code_tab_and_scrubber(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_text("name", "Name")
@render.text
def greeting():
    return f"Hello, {input.name()}"
"""
    reactlog = generate_reactlog(code, inputs={"name": "Ada"})
    input_step = next(
        index
        for index, event in enumerate(reactlog["events"])
        if event["event"] == "define" and event["node_id"] == "input:name"
    )

    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    source_panel = page.get_by_role("tabpanel", name="App code")
    expect(source_panel).to_be_hidden()

    page.get_by_role("tab", name="App code").click()
    expect(source_panel).to_be_visible()

    page.locator("#scrubber-range").fill(str(input_step))
    source_highlight = page.locator("#source-line-highlight")
    expect(source_highlight).to_be_visible()
    expect(source_highlight).to_have_attribute("data-line", "2")


def test_recording_video_tab(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_text("name", "Name")
@render.text
def greeting():
    return f"Hello, {input.name()}"
"""
    reactlog = generate_reactlog(code, video_path="demo.webm")
    page.set_content(
        format_reactlog_html(
            reactlog, source_code=code, video_path="/path/to/demo.webm"
        ),
        wait_until="domcontentloaded",
    )

    video_tab = page.get_by_role("tab", name="Recording")
    expect(video_tab).to_be_visible()

    video_tab.click()
    video_panel = page.get_by_role("tabpanel", name="Recording")
    expect(video_panel).to_be_visible()
    expect(page.locator("video")).to_be_visible()


def test_headless_recording_session(tmp_path: Path) -> None:
    app_file = tmp_path / "app.py"
    app_file.write_text(
        """from shiny.express import input, render, ui
ui.input_numeric("n", "Number", 10)
@render.text
def out():
    return f"N={input.n()}"
""",
        encoding="utf-8",
    )

    video_out = tmp_path / "test_session.webm"

    def record_actions(page: Page) -> None:
        page.wait_for_selector("input#n")
        page.fill("input#n", "42")
        page.wait_for_timeout(500)

    res = record_shiny_session(
        str(app_file),
        video_path=str(video_out),
        headless=True,
        record_script=record_actions,
    )

    assert res["success"] is True
    assert video_out.exists()
    assert len(res["actions"]) >= 1

    reactlog = generate_reactlog(
        app_file.read_text(),
        recorded_actions=res["actions"],
        video_path=str(video_out),
    )
    assert reactlog["success"] is True
    assert reactlog["trace_kind"] == "inferred_simulation_with_recorded_browser_events"


def test_phase_filter_and_skip_button(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("n", "N", 10)
@reactive.calc
def double_n():
    return input.n() * 2
@render.text
def out_txt():
    return f"Result: {double_n()}"
"""
    recorded_actions = [
        {"type": "input", "name": "n", "value": 25, "timestamp": 800},
        {"type": "output", "name": "out_txt", "timestamp": 1100},
    ]
    reactlog = generate_reactlog(
        code, recorded_actions=recorded_actions, video_path="demo.webm"
    )
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, video_path="demo.webm"),
        wait_until="domcontentloaded",
    )

    skip_btn = page.locator("#btn-skip-init")
    expect(skip_btn).to_be_visible()
    skip_btn.click()

    first_interact_step = reactlog["first_interaction_step"]
    expect(page.locator("#step-display")).to_have_text(
        f"Step {first_interact_step} / {reactlog['steps_total'] - 1}"
    )

    init_btn = page.locator("#phase-btn-init")
    init_btn.click()
    expect(page.locator(".event-item.is-current")).to_have_count(0)


def test_draggable_splitter_and_video_tab_resize(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("val", "Val", 10)
@render.text
def out():
    return f"V={input.val()}"
"""
    reactlog = generate_reactlog(code, video_path="demo.webm")
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, video_path="demo.webm"),
        wait_until="domcontentloaded",
    )

    resizer = page.locator("#split-resizer")
    expect(resizer).to_be_visible()

    # Keyboard resizing
    resizer.focus()
    page.keyboard.press("ArrowLeft")
    expect(resizer).to_have_attribute("aria-valuenow", "464")

    # Switching to recording tab widens sidebar
    video_tab = page.locator("#video-tab")
    video_tab.click()
    expect(page.locator("#video-panel")).to_be_visible()
    expect(page.locator("video")).to_be_visible()


def test_trace_timeline_scrubber_and_action_chips(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("multiplier", "Mult", 5)
@render.text
def res():
    return str(input.multiplier() * 10)
"""
    recorded_actions = [
        {"type": "input", "name": "multiplier", "value": 8, "timestamp": 1200},
        {"type": "output", "name": "res", "timestamp": 1600},
    ]
    reactlog = generate_reactlog(
        code, recorded_actions=recorded_actions, video_path="demo.webm"
    )
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, video_path="demo.webm"),
        wait_until="domcontentloaded",
    )

    trace_bar = page.locator("#trace-timeline-bar")
    expect(trace_bar).to_be_visible()
    expect(page.locator("#trace-playhead")).to_be_visible()
    expect(page.locator(".trace-chip")).to_have_count(3)
