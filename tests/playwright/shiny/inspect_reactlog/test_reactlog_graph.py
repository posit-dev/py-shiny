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
    expect(page.locator("#lane-inputs .trace-chip")).to_have_count(1)
    expect(page.locator("#lane-outputs .trace-chip")).to_have_count(2)
    expect(page.locator("#lane-calcs .trace-chip")).to_have_count(0)
    expect(page.locator(".trace-chip")).to_have_count(3)


def test_event_timeline_labels_initialization_and_recorded_actions(
    page: Page,
) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("multiplier", "Mult", 5)
@render.text
def res():
    return str(input.multiplier() * 10)
"""
    reactlog = generate_reactlog(
        code,
        recorded_actions=[
            {"type": "input", "name": "multiplier", "value": 8, "timestamp": 1200},
            {"type": "output", "name": "res", "timestamp": 1600},
        ],
        video_path="demo.webm",
    )
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, video_path="demo.webm"),
        wait_until="domcontentloaded",
    )

    phase_labels = page.locator(".event-phase-label")
    expect(phase_labels).to_have_count(2)
    expect(phase_labels.nth(0)).to_have_text("Initialization")
    expect(phase_labels.nth(1)).to_have_text("Recorded actions")


def test_event_items_can_be_activated_with_keyboard(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("multiplier", "Mult", 5)
@render.text
def res():
    return str(input.multiplier() * 10)
"""
    reactlog = generate_reactlog(code, inputs={"multiplier": 8})
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    target = page.locator(".event-item").nth(2)
    target_step = target.get_attribute("data-step")
    assert target_step is not None
    target.focus()
    expect(target).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator("#step-display")).to_have_text(
        f"Step {target_step} / {reactlog['steps_total'] - 1}"
    )


def test_event_inspector_describes_steps_without_graph_nodes(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("multiplier", "Mult", 5)
@render.text
def res():
    return str(input.multiplier() * 10)
"""
    reactlog = generate_reactlog(code, inputs={"multiplier": 8})
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    expect(page.locator("#insp-title")).to_have_text("session")
    expect(page.locator("#insp-type")).to_have_text("Initialization event")
    expect(page.locator("#insp-status")).to_have_text("active")


def test_video_playback_resumes_without_rewinding_after_last_graph_event(
    page: Page,
) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("multiplier", "Mult", 5)
@render.text
def res():
    return str(input.multiplier() * 10)
"""
    reactlog = generate_reactlog(
        code,
        recorded_actions=[
            {"type": "input", "name": "multiplier", "value": 8, "timestamp": 1200},
            {"type": "output", "name": "res", "timestamp": 1600},
        ],
        video_path="demo.webm",
    )
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, video_path="demo.webm"),
        wait_until="domcontentloaded",
    )

    page.locator("#session-video").evaluate("""video => {
            let mediaTime = 2;
            Object.defineProperties(video, {
                currentTime: {
                    configurable: true,
                    get: () => mediaTime,
                    set: value => { mediaTime = value; },
                },
                duration: { configurable: true, get: () => 10 },
                ended: { configurable: true, get: () => false },
                paused: { configurable: true, get: () => true },
            });
            video.play = () => Promise.resolve();
        }""")
    page.evaluate(f"seekTo({reactlog['steps_total'] - 1}, true)")
    page.locator("#session-video").evaluate("video => { video.currentTime = 2; }")

    page.locator("#btn-play").click()

    assert page.locator("#session-video").evaluate("video => video.currentTime") == 2


def test_video_frame_callback_updates_graph_between_timeupdate_events(
    page: Page,
) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("multiplier", "Mult", 5)
@render.text
def res():
    return str(input.multiplier() * 10)
"""
    reactlog = generate_reactlog(
        code,
        recorded_actions=[
            {"type": "input", "name": "multiplier", "value": 8, "timestamp": 1200},
            {"type": "output", "name": "res", "timestamp": 1600},
        ],
        video_path="demo.webm",
    )
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, video_path="demo.webm"),
        wait_until="domcontentloaded",
    )

    page.locator("#session-video").evaluate("""video => {
            Object.defineProperties(video, {
                paused: { configurable: true, get: () => false },
                ended: { configurable: true, get: () => false },
            });
            video.requestVideoFrameCallback = callback => {
                window.__videoFrameCallback = callback;
                return 1;
            };
            video.dispatchEvent(new Event('play'));
        }""")

    assert page.evaluate("Boolean(window.__videoFrameCallback)") is True
    page.evaluate("window.__videoFrameCallback(performance.now(), { mediaTime: 1.25 })")
    expect(page.locator("#step-display")).to_have_text(
        f"Step {reactlog['first_interaction_step']} / {reactlog['steps_total'] - 1}"
    )


def test_theme_toggle_button_and_modes(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("val", "Val", 10)
@render.text
def out():
    return f"V={input.val()}"
"""
    reactlog = generate_reactlog(code)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, theme="dark"),
        wait_until="domcontentloaded",
    )

    html_el = page.locator("html")
    expect(html_el).to_have_attribute("data-theme", "dark")

    theme_btn = page.locator("#btn-theme-toggle")
    expect(theme_btn).to_be_visible()
    theme_btn.click()

    expect(html_el).to_have_attribute("data-theme", "light")

    theme_btn.click()
    expect(html_el).to_have_attribute("data-theme", "dark")


def test_in_browser_load_reactlog_json(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("val", "Val", 10)
@render.text
def out():
    return f"V={input.val()}"
"""
    reactlog = generate_reactlog(code)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    r_reactlog_data = {
        "version": "1.0",
        "session": "test_sess",
        "log": [
            {"action": "define", "id": "input:alpha", "label": "alpha", "type": "observable", "time": 0.1},
            {"action": "define", "id": "calc:beta", "label": "beta", "type": "calc", "time": 0.2},
            {"action": "dependsOn", "id": "calc:beta", "dependsOn": "input:alpha", "time": 0.3},
            {"action": "define", "id": "output:gamma", "label": "gamma", "type": "observer", "time": 0.4},
            {"action": "dependsOn", "id": "output:gamma", "dependsOn": "calc:beta", "time": 0.5},
        ]
    }

    page.evaluate("data => loadReactlogObject(data)", r_reactlog_data)

    expect(page.locator("#stat-nodes")).to_have_text("Nodes: 3")
    expect(page.locator("#stat-edges")).to_have_text("Edges: 2")
    expect(page.locator(".graph-node")).to_have_count(3)
    expect(page.locator(".graph-edge")).to_have_count(2)
