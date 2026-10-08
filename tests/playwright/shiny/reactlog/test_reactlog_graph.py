from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Literal

from playwright.sync_api import Locator, Page, expect

from shiny.reactive._reactlog._viewer import format_reactlog_html, load_reactlog_json
from tests.pytest._reactlog_fixtures import record_export

PNG = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a7S8AAAAASUVORK5CYII="


def load_graph_report(
    page: Page,
    html: str,
    *,
    wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = "load",
) -> None:
    """Open the graph and inspector explicitly for tests of those surfaces."""
    page.set_default_timeout(5000)
    page.set_content(html, wait_until=wait_until)
    page.locator("#btn-mode-full").click()
    page.locator("#btn-toggle-inspector").click()
    page.locator("#event-history").evaluate("el => el.open = true")
    page.locator("#flush-card").evaluate("el => el.open = true")


def graph_node(page: Page, selector: str) -> Locator:
    if page.locator("#sidebar").is_visible():
        page.get_by_role("button", name="Close Inspector", exact=True).click()
    return page.locator(selector)


def _visible(*ids: str) -> dict[str, bool]:
    """Client data that marks outputs visible, so a mock session renders them."""
    return {f".clientdata_output_{i}_hidden": False for i in ids}


def _export(
    tmp_path: Path,
    code: str,
    steps: list[dict[str, Any]],
    *,
    files: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Record a real session of `server` in `code`, written to tmp_path/app.py so
    recorded lines and `sources` match `code`. `files` are importable siblings."""
    for name, text in {**(files or {}), "app.py": code}.items():
        (tmp_path / name).write_text(text)
    sys.path.insert(0, str(tmp_path))
    try:
        namespace: dict[str, Any] = {}
        exec(compile(code, str(tmp_path / "app.py"), "exec"), namespace)
        return record_export(namespace["server"], steps)
    finally:
        sys.path.remove(str(tmp_path))
        for name in files or {}:
            sys.modules.pop(Path(name).stem, None)


def _record(
    tmp_path: Path,
    code: str,
    steps: list[dict[str, Any]],
    *,
    files: dict[str, str] | None = None,
) -> dict[str, Any]:
    return load_reactlog_json(_export(tmp_path, code, steps, files=files))


def _id(report: dict[str, Any], label: str) -> str:
    return next(n["id"] for n in report["nodes"] if n["label"] == label)


def _node(report: dict[str, Any], label: str) -> str:
    return f'.graph-node[data-id="{_id(report, label)}"]'


def _step(report: dict[str, Any], event: str, label: str, value: Any = None) -> str:
    """Index of the first `event` on node `label` (with `value`, if given)."""
    return str(
        next(
            i
            for i, e in enumerate(report["events"])
            if e["event"] == event
            and e.get("node_label") == label
            and (value is None or e.get("value") == str(value))
        )
    )


def _add_plots(export: dict[str, Any], plots: list[tuple[str, str]]) -> None:
    """Append one plot snapshot per (output label, alt), a second apart, the way
    recorded browser snapshots attach to a recorded output."""
    log = export["log"]
    defines = {e["label"]: e for e in log if e["action"] == "define"}
    for i, (label, alt) in enumerate(plots, start=1):
        log.append(
            {
                "action": "valueChange",
                "reactId": defines[label]["reactId"],
                "label": label,
                "type": "output",
                "time": log[-1]["time"] + i,
                "plot": {"src": PNG, "alt": alt},
            }
        )


def _delay_from(export: dict[str, Any], label: str, value: Any, seconds: float) -> None:
    """Shift the log from `label`'s change to `value` onward, as if the user acted
    `seconds` later."""
    log = export["log"]
    start = next(
        i
        for i, e in enumerate(log)
        if e["action"] == "valueChange"
        and e.get("label") == label
        and str(e.get("value")) == str(value)
    )
    for entry in log[start:]:
        entry["time"] += seconds


_XY_CODE = """from shiny import reactive, render

def server(input, output, session):
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
_XY_STEPS: list[dict[str, Any]] = [{"x": 1, "y": 2, **_visible("result", "other")}]

_MULT_CODE = """from shiny import render

def server(input, output, session):
    @render.text
    def res():
        return str(input.multiplier() * 10)
"""
_MULT_STEPS: list[dict[str, Any]] = [
    {"multiplier": 5, **_visible("res")},
    {"multiplier": 8},
]

_VAL_CODE = """from shiny import render

def server(input, output, session):
    @render.text
    def out():
        return f"V={input.val()}"
"""
_VAL_STEPS: list[dict[str, Any]] = [{"val": 10, **_visible("out")}]


def test_graph_elements_visible_on_initialization(page: Page, tmp_path: Path) -> None:
    reactlog = _record(tmp_path, _XY_CODE, _XY_STEPS)
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=_XY_CODE),
        wait_until="domcontentloaded",
    )

    # x, y, doubled, result, other, and the two outputs' `.clientdata_*_hidden`.
    nodes = page.locator(".graph-node")
    assert nodes.count() == 7

    edges = page.locator(".graph-edge")
    assert edges.count() == 3

    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('.graph-edge')).every(edge => parseFloat(window.getComputedStyle(edge).opacity) > 0.5)"
    )


def test_hover_highlights_connections(page: Page, tmp_path: Path) -> None:
    reactlog = _record(tmp_path, _XY_CODE, _XY_STEPS)
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=_XY_CODE),
        wait_until="domcontentloaded",
    )

    graph_node(page, _node(reactlog, "reactive.calc doubled")).hover()
    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('.graph-edge')).some(edge => parseFloat(edge.style.opacity) === 1)"
    )

    page.locator(".toolbar").hover()
    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('.graph-edge')).every(edge => parseFloat(edge.style.opacity) >= 0.6)"
    )


def test_selected_lineage_stays_focused_during_hover_and_playback(
    page: Page, tmp_path: Path
) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def doubled():
        return input.x() * 2

    @render.text
    def result():
        return doubled()

    @render.text
    def sibling():
        return input.x()

    @render.text
    def other():
        return input.y()
"""
    report = _record(
        tmp_path, code, [{"x": 1, "y": 2, **_visible("result", "sibling", "other")}]
    )
    other = _id(report, "output other")
    load_graph_report(page, format_reactlog_html(report, code))
    graph_node(page, _node(report, "reactive.calc doubled")).click()
    page.locator(".toolbar").hover()
    # 9 nodes (incl. 3 `.clientdata_*_hidden`); only x -> doubled -> result stay lit.
    expect(page.locator(".graph-node.is-dimmed")).to_have_count(6)
    expect(page.locator(".graph-edge.is-dimmed")).to_have_count(2)
    expect(page.locator(_node(report, "input.x"))).not_to_have_class(
        re.compile("is-dimmed")
    )
    graph_node(page, _node(report, "output other")).hover()
    expect(page.locator(".graph-node.is-dimmed")).to_have_count(6)
    # An unrelated active edge must not override the selection's muted styling.
    step = next(
        i
        for i, e in enumerate(report["events"])
        if e["event"] == "dependsOn" and e.get("edge_to") == other
    )
    page.evaluate(f"seekTo({step})")
    expect(page.locator("#insp-title")).to_contain_text("doubled")
    edge = page.locator(f'.graph-edge[data-to="{other}"]')
    expect(edge).to_have_css("opacity", "0.15")
    expect(edge).to_have_css("animation-name", "none")
    page.locator(_node(report, "output other")).focus()
    page.keyboard.press("Enter")
    expect(page.locator("#insp-title")).to_contain_text("other")
    page.keyboard.press("Escape")
    expect(page.locator(".is-dimmed")).to_have_count(0)
    graph_node(page, _node(report, "reactive.calc doubled")).click()
    page.get_by_role("button", name="Clear node selection", exact=True).click()
    expect(page.locator(".is-dimmed")).to_have_count(0)


def test_root_and_module_plots_remain_distinct_and_follow_selected_time(
    page: Page, tmp_path: Path
) -> None:
    code = """from shiny import module, render

@module.server
def panel(input, output, session):
    @render.plot
    def chart():
        input.n()

def server(input, output, session):
    panel("sales")

    @render.plot
    def chart():
        input.n()
"""
    export = _export(
        tmp_path, code, [{"n": 1, "sales-n": 1, **_visible("chart", "sales-chart")}]
    )
    _add_plots(
        export,
        [
            ("output chart", "App plot"),
            ("output sales:chart", "Module plot"),
            ("output chart", "Updated app plot"),
        ],
    )
    report = load_reactlog_json(export)
    steps = [i for i, e in enumerate(report["events"]) if e.get("plot")]
    load_graph_report(page, format_reactlog_html(report, code))
    expect(page.locator(".app-box")).to_contain_text("App (no namespace)")
    root_chart = _node(report, "output chart")
    page.locator(root_chart).click()
    expect(page.locator("#insp-plot-image")).to_be_hidden()
    page.evaluate(f"seekTo({steps[0]})")
    expect(page.locator("#insp-plot-image")).to_have_attribute("alt", "App plot")
    page.locator('.module-box[data-module="sales"] text').dblclick()
    expect(page.locator('.graph-node[data-id="module:sales"]')).to_have_class(
        re.compile("is-dimmed")
    )
    expect(page.locator(root_chart)).to_be_visible()
    page.evaluate(f"seekTo({steps[2]})")
    expect(page.locator("#insp-plot-image")).to_have_attribute(
        "alt", "Updated app plot"
    )
    page.evaluate("seekTo(0)")
    expect(page.locator("#insp-plot-image")).to_be_hidden()
    page.locator('.graph-node[data-id="module:sales"]').dblclick()
    graph_node(page, _node(report, "output sales:chart")).click()
    page.evaluate(f"seekTo({steps[1]})")
    expect(page.locator("#insp-plot-image")).to_have_attribute("alt", "Module plot")


def test_app_code_tab_and_scrubber(page: Page, tmp_path: Path) -> None:
    code = """from shiny import render

def server(input, output, session):
    @render.text
    def greeting():
        return f"Hello, {input.name()}"
"""
    reactlog = _record(tmp_path, code, [{"name": "Ada", **_visible("greeting")}])
    # Recorded inputs carry no source line; the output's definition does.
    output_step = _step(reactlog, "define", "output greeting")

    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    source_panel = page.get_by_role("tabpanel", name="App code")
    expect(source_panel).to_be_hidden()

    page.get_by_role("tab", name="App code").click()
    expect(source_panel).to_be_visible()

    page.locator("#scrubber-range").fill(output_step)
    source_highlight = page.locator("#source-line-highlight")
    expect(source_highlight).to_be_visible()
    expect(source_highlight).to_have_attribute(
        "data-line", str(code.splitlines().index("    def greeting():") + 1)
    )


def test_phase_filter_and_skip_button(page: Page, tmp_path: Path) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def double_n():
        return input.n() * 2

    @render.text
    def out_txt():
        return f"Result: {double_n()}"
"""
    reactlog = _record(tmp_path, code, [{"n": 10, **_visible("out_txt")}, {"n": 25}])
    load_graph_report(
        page,
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

    phase_select = page.locator("#phase-filter-select")
    expect(phase_select).to_be_visible()
    phase_select.select_option("init")
    expect(page.locator(".event-item.is-current")).to_have_count(0)


def test_event_timeline_labels_initialization_and_recorded_actions(
    page: Page, tmp_path: Path
) -> None:
    reactlog = _record(tmp_path, _MULT_CODE, _MULT_STEPS)
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=_MULT_CODE, video_path="demo.webm"),
        wait_until="domcontentloaded",
    )

    phase_labels = page.locator(".event-phase-label")
    expect(phase_labels).to_have_count(2)
    expect(phase_labels.nth(0)).to_have_text("Initialization")
    expect(phase_labels.nth(1)).to_have_text("Recorded actions")


def test_event_items_can_be_activated_with_keyboard(page: Page, tmp_path: Path) -> None:
    reactlog = _record(tmp_path, _MULT_CODE, _MULT_STEPS)
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=_MULT_CODE),
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


def test_event_inspector_describes_steps_without_graph_nodes(
    page: Page, tmp_path: Path
) -> None:
    reactlog = _record(tmp_path, _MULT_CODE, _MULT_STEPS)
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=_MULT_CODE),
        wait_until="domcontentloaded",
    )

    # The end of the initial flush belongs to no node.
    page.keyboard.press("Escape")
    step = next(
        i for i, e in enumerate(reactlog["events"]) if e["event"] == "queueEmpty"
    )
    page.evaluate(f"seekTo({step})")
    expect(page.locator("#insp-title")).to_have_text("queueEmpty")
    expect(page.locator("#insp-type")).to_have_text("Initialization event")
    expect(page.locator("#insp-status")).to_have_text("active")


def test_video_playback_resumes_without_rewinding_after_last_graph_event(
    page: Page, tmp_path: Path
) -> None:
    reactlog = _record(tmp_path, _MULT_CODE, _MULT_STEPS)
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=_MULT_CODE, video_path="demo.webm"),
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
    page: Page, tmp_path: Path
) -> None:
    export = _export(tmp_path, _MULT_CODE, _MULT_STEPS)
    # The user changes `multiplier` 2s into the recording.
    _delay_from(export, "input.multiplier", 8, seconds=2)
    reactlog = load_reactlog_json(export)
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=_MULT_CODE, video_path="demo.webm"),
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
    # The last event before the change: the end of the initial session burst.
    before_change = max(
        i for i, e in enumerate(reactlog["events"]) if e["time_sec"] <= 1.25
    )
    assert before_change < reactlog["steps_total"] - 1
    expect(page.locator("#step-display")).to_have_text(
        f"Step {before_change} / {reactlog['steps_total'] - 1}"
    )


def test_theme_toggle_button_and_modes(page: Page, tmp_path: Path) -> None:
    reactlog = _record(tmp_path, _VAL_CODE, _VAL_STEPS)
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=_VAL_CODE, theme="dark"),
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


def test_in_browser_load_reactlog_json(page: Page, tmp_path: Path) -> None:
    reactlog = _record(tmp_path, _VAL_CODE, _VAL_STEPS)
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=_VAL_CODE),
        wait_until="domcontentloaded",
    )

    r_reactlog_data = {
        "version": "1.0",
        "session": "test_sess",
        "log": [
            {
                "action": "define",
                "id": "input:alpha",
                "label": "alpha",
                "type": "observable",
                "time": 0.1,
            },
            {
                "action": "define",
                "id": "calc:beta",
                "label": "beta",
                "type": "calc",
                "time": 0.2,
            },
            {
                "action": "dependsOn",
                "id": "calc:beta",
                "dependsOn": "input:alpha",
                "time": 0.3,
            },
            {
                "action": "define",
                "id": "output:gamma",
                "label": "gamma",
                "type": "observer",
                "time": 0.4,
            },
            {
                "action": "dependsOn",
                "id": "output:gamma",
                "dependsOn": "calc:beta",
                "time": 0.5,
            },
        ],
    }

    page.evaluate("data => loadReactlogObject(data)", r_reactlog_data)

    expect(page.locator("#filter-node-count")).to_have_text("3 of 3 nodes")
    expect(page.locator(".graph-edge")).to_have_count(2)
    expect(page.locator(".graph-node")).to_have_count(3)
    expect(page.locator(".graph-edge")).to_have_count(2)


def test_why_did_this_run_causal_inspector(page: Page, tmp_path: Path) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def doubled():
        return input.x() * 2

    @render.text
    def result():
        return str(doubled())
"""
    reactlog = _record(tmp_path, code, [{"x": 10, "y": 20, **_visible("result")}])
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    graph_node(page, _node(reactlog, "reactive.calc doubled")).click()

    why_title = page.locator("#why-title")
    expect(why_title).to_contain_text("Why did reactive.calc doubled run?")

    why_story = page.locator("#why-story")
    expect(why_story).to_contain_text("doubled")

    flow_pills = page.locator("#why-cascade-flow .flow-node-pill")
    expect(flow_pills).to_have_count(2)
    expect(flow_pills.first).to_have_text("input.x")
    expect(flow_pills.last).to_have_text("reactive.calc doubled")

    upstream_pills = page.locator("#insp-upstream-list .conn-pill")
    expect(upstream_pills).to_have_count(1)
    expect(upstream_pills.first).to_have_text("input.x")

    downstream_pills = page.locator("#insp-downstream-list .conn-pill")
    expect(downstream_pills).to_have_count(1)
    expect(downstream_pills.first).to_have_text("output result")


def test_selection_keeps_all_nodes_visible(page: Page, tmp_path: Path) -> None:
    reactlog = _record(tmp_path, _XY_CODE, _XY_STEPS)
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=_XY_CODE),
        wait_until="domcontentloaded",
    )

    # 5 app nodes plus the two outputs' `.clientdata_*_hidden`.
    expect(page.locator(".graph-node")).to_have_count(7)

    graph_node(page, _node(reactlog, "reactive.calc doubled")).click()

    expect(page.locator(".path-controls")).to_have_count(0)
    expect(page.locator(".graph-node")).to_have_count(7)
    expect(page.locator(".graph-node:not(.is-dimmed)")).to_have_count(3)
    graph_node(page, _node(reactlog, "input.x")).click()
    expect(page.locator(".graph-node:not(.is-dimmed)")).to_have_count(3)
    graph_node(page, _node(reactlog, "output other")).click()
    expect(page.locator(".graph-node:not(.is-dimmed)")).to_have_count(2)
    expect(page.locator(".graph-node")).to_have_count(7)
    expect(page.locator(_node(reactlog, "output other"))).to_have_class(
        re.compile("is-selected")
    )


def test_actions_story_tab_and_inline_code_drawer(page: Page, tmp_path: Path) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def calc_b():
        return input.val() + 1

    @render.text
    def out():
        return str(calc_b())
"""
    reactlog = _record(tmp_path, code, [{"val": 5, **_visible("out")}, {"val": 42}])
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    expect(page.locator("#actions-tab, #timeline-tab")).to_have_count(0)

    graph_node(page, _node(reactlog, "reactive.calc calc_b")).click()
    drawer_toggle = page.locator("#btn-toggle-source-drawer")
    expect(drawer_toggle).to_be_visible()

    source_code = page.locator("#insp-source-code")
    expect(source_code).to_be_hidden()

    drawer_toggle.click()
    expect(source_code).to_be_visible()
    expect(source_code).to_contain_text("def calc_b():")


def test_id_lineage_filter_and_timeline_preservation(
    page: Page, tmp_path: Path
) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def c():
        return input.x() * 2

    @render.text
    def o():
        return str(c())

    @render.text
    def separate_out():
        return str(input.y())
"""
    reactlog = _record(
        tmp_path, code, [{"x": 1, "y": 10, **_visible("o", "separate_out")}]
    )
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    expect(page.locator(".graph-node")).to_have_count(7)

    search = page.locator("#search-input")
    search.fill(f"id:{_id(reactlog, 'reactive.calc c')}")
    expect(page.locator(".graph-node")).to_have_count(3)
    expect(page.locator(_node(reactlog, "input.x"))).to_be_visible()
    expect(page.locator(_node(reactlog, "reactive.calc c"))).to_be_visible()
    expect(page.locator(_node(reactlog, "output o"))).to_be_visible()
    expect(page.locator(_node(reactlog, "input.y"))).to_have_count(0)
    expect(page.locator(_node(reactlog, "output separate_out"))).to_have_count(0)

    page.get_by_role("button", name="Step forward").click()
    expect(page.locator(".graph-node")).to_have_count(3)

    page.get_by_role("button", name="Reset view", exact=True).click()
    expect(page.locator(".graph-node")).to_have_count(7)


def test_multi_parent_dag_tree_and_single_target_synchronization(
    page: Page, tmp_path: Path
) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def calc_a():
        return input.a() * 10

    @reactive.calc
    def calc_b():
        return input.b() * 20

    @render.text
    def merged():
        return f"Sum: {calc_a() + calc_b()}"
"""
    reactlog = _record(tmp_path, code, [{"a": 1, "b": 2, **_visible("merged")}])
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    graph_node(page, _node(reactlog, "output merged")).click()

    expect(page.locator("#insp-title")).to_contain_text("merged")

    why_title = page.locator("#why-title")
    expect(why_title).to_contain_text("Why did output merged render?")

    dag_pills = page.locator("#why-cascade-flow .flow-node-pill")
    expect(dag_pills).to_have_count(3)

    why_story = page.locator("#why-story")
    expect(why_story).to_contain_text("Immediate causes:")
    expect(why_story).to_contain_text("reactive.calc calc_a")
    expect(why_story).to_contain_text("reactive.calc calc_b")


_PRICE_CODE = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def subtotal():
        return input.price() * 2

    @render.text
    def summary():
        return f"Subtotal: {subtotal()}"
"""


def test_humanized_timeline_dynamic_verbs_and_causal_summary(
    page: Page, tmp_path: Path
) -> None:
    reactlog = _record(
        tmp_path, _PRICE_CODE, [{"price": 25, **_visible("summary")}, {"price": 30}]
    )
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=_PRICE_CODE),
        wait_until="domcontentloaded",
    )

    page.evaluate(f"seekTo({_step(reactlog, 'valueChange', 'input.price', 30)})")
    expect(page.locator("#active-flush-label")).to_contain_text("price: 25 → 30")
    expect(page.locator("#causal-summary-banner")).to_have_count(0)

    # 3. Dynamic Why Question for Input
    graph_node(page, _node(reactlog, "input.price")).click()
    why_title = page.locator("#why-title")
    expect(why_title).to_contain_text("Why did input.price change?")

    # 4. Dynamic Why Question for Calc
    graph_node(page, _node(reactlog, "reactive.calc subtotal")).click()
    expect(why_title).to_contain_text("Why did reactive.calc subtotal run?")

    # 5. Dynamic Why Question for Output
    graph_node(page, _node(reactlog, "output summary")).click()
    expect(why_title).to_contain_text("Why did output summary render?")

    # 6. Streamlined Toolbar & Phase Filter
    phase_select = page.locator("#phase-filter-select")
    expect(phase_select).to_be_visible()


def test_init_story_counts_recorded_calcs_and_outputs(
    page: Page, tmp_path: Path
) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def doubled():
        return input.x() * 2

    @render.text
    def result():
        return str(doubled())
"""
    reactlog = _record(tmp_path, code, [{"x": 1, **_visible("result")}, {"x": 2}])
    page.set_content(format_reactlog_html(reactlog, source_code=code))
    page.evaluate(f"seekTo({_step(reactlog, 'enter', 'output result')})")
    page.get_by_role("button", name="Node details", exact=True).click()
    page.locator("#flush-card").evaluate("el => el.open = true")
    expect(page.locator("#flush-card-calcs")).to_have_text("1 calcs re-evaluated")
    expect(page.locator("#flush-card-outputs")).to_have_text("1 outputs flushed")


def test_empty_graph_shows_summary_notice(page: Page) -> None:
    reactlog = load_reactlog_json({"log": []})
    reactlog["summary"] = "No session selected."
    page.set_content(format_reactlog_html(reactlog, ""))
    expect(page.locator("#active-flush-label")).to_have_text("No session selected.")
    expect(page.locator("#active-flush-label")).to_be_visible()


def test_action_scoped_causal_story_and_did_not_run_explanation(
    page: Page, tmp_path: Path
) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def subtotal():
        return input.price() * input.units()

    @reactive.calc
    def discount():
        return 0.1 if input.client() == "Acme" else 0.0

    @render.text
    def order_summary():
        return f"Order: {subtotal()}"

    @render.text
    def client_badge():
        return f"Client: {input.client()} (Discount: {discount()})"
"""
    reactlog = _record(
        tmp_path,
        code,
        [
            {
                "price": 25,
                "units": 10,
                "client": "Acme",
                **_visible("order_summary", "client_badge"),
            },
            {"price": 30},
        ],
    )
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    # 1. Go to the price action burst
    page.evaluate(f"seekTo({_step(reactlog, 'valueChange', 'input.price', 30)})")

    expect(page.locator("#active-flush-label")).to_contain_text("price: 25 → 30")

    # 3. Clicking the order summary output shows why it rendered in this burst
    graph_node(page, _node(reactlog, "output order_summary")).click()
    why_title = page.locator("#why-title")
    expect(why_title).to_contain_text("Why did output order_summary render?")
    why_story = page.locator("#why-story")
    expect(why_story).to_contain_text("subtotal")

    # Selecting an output preserves the full graph but mutes the other branch:
    # 7 app nodes plus 2 `.clientdata_*_hidden`; price, units, subtotal and
    # order_summary stay lit.
    expect(page.locator(".graph-node")).to_have_count(9)
    expect(page.locator(".graph-node.is-dimmed")).to_have_count(5)

    # 5. Clicking unaffected node (client) shows did not change in this action
    graph_node(page, _node(reactlog, "input.client")).click()
    expect(why_title).to_contain_text("input.client did not change")
    expect(page.locator("#why-story")).to_contain_text("Did not change during")

    # The muted input is still clickable and switches the focused branch.
    expect(page.locator(".graph-node")).to_have_count(9)
    expect(page.locator(".graph-node.is-dimmed")).to_have_count(6)


def test_malicious_node_id_no_code_execution_xss_protection(
    page: Page, tmp_path: Path
) -> None:
    reactlog = _record(tmp_path, _VAL_CODE, _VAL_STEPS)
    malicious_json = {
        "version": "1.0",
        "session": "pwn_test",
        "nodes": [
            {
                "id": "calc:safe_node",
                "label": "calc:safe_node",
                "role": "conductor",
                "type": "calc",
            },
            {
                "id": "output:xss'); window.__pwned=1; ('",
                "label": "<img src=x onerror=window.__pwned=1>",
                "role": "observer",
                "type": "output",
            },
        ],
        "edges": [
            {
                "from": "calc:safe_node",
                "to": "output:xss'); window.__pwned=1; ('",
            }
        ],
        "events": [
            {
                "step": 0,
                "event": "define",
                "action": "define",
                "id": "calc:safe_node",
                "node_id": "calc:safe_node",
                "phase": "init",
                "provenance": "observed",
            },
            {
                "step": 1,
                "event": "define",
                "action": "define",
                "id": "output:xss'); window.__pwned=1; ('",
                "node_id": "output:xss'); window.__pwned=1; ('",
                "phase": "init",
                "provenance": "observed",
            },
            {
                "step": 2,
                "event": "dependsOn",
                "action": "dependsOn",
                "edge_from": "calc:safe_node",
                "edge_to": "output:xss'); window.__pwned=1; ('",
                "node_id": "output:xss'); window.__pwned=1; ('",
                "phase": "init",
                "provenance": "observed",
            },
        ],
    }

    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=_VAL_CODE),
        wait_until="domcontentloaded",
    )
    page.evaluate("data => loadReactlogObject(data)", malicious_json)

    # Click nodes and buttons to trigger any handlers
    page.locator('.graph-node[data-id="calc:safe_node"]').click()
    is_pwned = page.evaluate("() => Boolean(window.__pwned)")
    assert is_pwned is False


def test_app_code_tab_and_drawer_show_line_numbers(page: Page, tmp_path: Path) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def double_val():
        return input.val() * 2

    @render.text
    def out():
        return f"Result: {double_val()}"
"""
    reactlog = _record(tmp_path, code, [{"val": 10, **_visible("out")}])
    load_graph_report(
        page,
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    # 1. Check App code tab line numbers
    page.get_by_role("tab", name="App code").click()
    source_panel = page.get_by_role("tabpanel", name="App code")
    expect(source_panel).to_be_visible()

    line_nums = page.locator("#source-panel .source-line-num")
    expect(line_nums.first).to_have_text("1")
    expect(line_nums.nth(3)).to_have_text("4")

    # 2. Check inline drawer line numbers: the snippet starts at the recorded line.
    page.get_by_role("button", name="Node details", exact=True).click()
    graph_node(page, _node(reactlog, "reactive.calc double_val")).click()
    page.locator("#btn-toggle-source-drawer").click()

    drawer_line_nums = page.locator("#insp-source-code .source-line-num")
    expect(drawer_line_nums.first).to_have_text(
        str(code.splitlines().index("    def double_val():") + 1)
    )


def test_r_import_search_preserves_all_nodes(page: Page) -> None:
    raw = [
        {"action": "invalidateStart", "reactId": "r2"},
        {
            "action": "define",
            "reactId": "r1$x",
            "type": "reactiveValuesKey",
            "label": "input$x",
        },
        {
            "action": "define",
            "reactId": "r2",
            "type": "observable",
            "label": "doubled_value",
        },
        {
            "action": "define",
            "reactId": "r3",
            "type": "observer",
            "label": "output$result",
        },
        {"action": "define", "reactId": "r4", "type": "observer", "label": "unrelated"},
        {"action": "dependsOn", "reactId": "r2", "depOnReactId": "r1$x"},
        {"action": "dependsOn", "reactId": "r3", "depOnReactId": "r2"},
        {"action": "dependsOn", "reactId": "r4", "depOnReactId": "r1$x"},
    ]
    load_graph_report(
        page, format_reactlog_html(load_reactlog_json(raw), source_code="")
    )
    # Exercise the separate browser file-import normalizer as well.
    page.evaluate("raw => loadReactlogObject(raw)", raw)
    expect(page.locator('.graph-node[data-id="r1$x"]')).to_have_attribute(
        "data-role", "source"
    )
    expect(page.locator('.graph-node[data-id="r2"]')).to_have_attribute(
        "data-role", "conductor"
    )
    expect(page.locator('.graph-node[data-id="r3"]')).to_have_attribute(
        "data-role", "observer"
    )
    page.locator("#search-input").fill("dblvl")
    expect(page.locator("#search-results button")).to_have_count(1)
    page.locator("#search-input").fill("id:r2")
    page.locator("#search-results button").click()
    expect(page.locator(".graph-node")).to_have_count(3)
    expect(page.locator('.graph-node[data-id="r4"]')).to_have_count(0)
    expect(page.locator("#search-results")).to_be_hidden()
    page.get_by_role("button", name="Reset view", exact=True).click()
    expect(page.locator(".graph-node")).to_have_count(4)
    page.locator("#search-input").fill("no match xyz")
    expect(page.locator("#search-results")).to_contain_text("0 matches")
    page.locator("#search-input").press("Escape")
    expect(page.locator(".graph-node")).to_have_count(4)


def test_fit_large_graph(page: Page) -> None:
    raw = [
        {
            "action": "define",
            "reactId": f"r{i}",
            "type": "observable",
            "label": f"reactive {i}",
        }
        for i in range(200)
    ]
    load_graph_report(
        page, format_reactlog_html(load_reactlog_json(raw), source_code="")
    )
    page.get_by_role("button", name="Fit graph to view", exact=True).click()
    bounds = page.evaluate("""() => {
        const svg = document.getElementById('reactlog-svg').getBoundingClientRect();
        const graph = document.getElementById('viewport-g').getBoundingClientRect();
        return {fits: graph.top >= svg.top && graph.bottom <= svg.bottom && graph.left >= svg.left && graph.right <= svg.right, zoom: zoomLevel};
    }""")
    assert bounds["fits"]
    assert bounds["zoom"] < 0.4


_X_RESULT_CODE = """from shiny import render

def server(input, output, session):
    @render.text
    def result():
        return str(input.x())
"""


def test_search_keyboard_and_reset_view(page: Page, tmp_path: Path) -> None:
    report = _record(tmp_path, _X_RESULT_CODE, [{"x": 1, **_visible("result")}])
    load_graph_report(page, format_reactlog_html(report, _X_RESULT_CODE))
    search = page.locator("#search-input")
    search.fill(f"id:{_id(report, 'output result')}")
    search.press("ArrowDown")
    expect(page.locator("#search-results button")).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator("#search-results")).to_be_hidden()
    page.get_by_role("button", name="Reset view", exact=True).click()
    # input.x, output result, and the output's `.clientdata_*_hidden`.
    expect(page.locator(".graph-node")).to_have_count(3)
    search.fill("unfindablenode")
    expect(page.locator("#search-results")).to_contain_text(
        "0 matches. Try a node name"
    )
    search.press("Escape")
    expect(search).to_be_focused()
    expect(page.locator(".graph-node")).to_have_count(3)


def test_narrow_report_keeps_graph_and_controls_accessible(
    page: Page, tmp_path: Path
) -> None:
    report = _record(tmp_path, _X_RESULT_CODE, [{"x": 1, **_visible("result")}])
    original_viewport = page.viewport_size
    try:
        for width in (390, 768):
            page.set_viewport_size({"width": width, "height": 844})
            load_graph_report(page, format_reactlog_html(report, _X_RESULT_CODE))
            bounds = page.evaluate("""() => {
                const graph = document.getElementById('graph-container').getBoundingClientRect();
                const sidebar = document.getElementById('sidebar').getBoundingClientRect();
                const controls = document.querySelector('.toolbar').getBoundingClientRect();
                return {width: document.documentElement.scrollWidth,
                    viewport: innerWidth, graphWidth: graph.width,
                    overlay: sidebar.top >= graph.top && sidebar.bottom <= graph.bottom,
                    controlsFit: controls.right <= innerWidth};
            }""")
            assert bounds["width"] <= bounds["viewport"]
            assert bounds["graphWidth"] == width - 40
            assert bounds["overlay"]
            assert bounds["controlsFit"]
            # `output result` and its `.clientdata_output_result_hidden`.
            page.locator("#search-input").fill("result")
            expect(page.locator("#search-results button")).to_have_count(2)
    finally:
        if original_viewport:
            page.set_viewport_size(original_viewport)


def test_dependency_depth_and_cycles(page: Page, tmp_path: Path) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def subtotal():
        return input.units() * input.price()

    @reactive.calc
    def discount_multiplier():
        return input.discount()

    @reactive.calc
    def total_revenue():
        return subtotal() * discount_multiplier()

    @render.text
    def result():
        return total_revenue()
"""
    report = _record(
        tmp_path, code, [{"units": 2, "price": 3, "discount": 1, **_visible("result")}]
    )
    load_graph_report(page, format_reactlog_html(report, code))
    positions = page.locator(".graph-node").evaluate_all(
        "nodes => Object.fromEntries(nodes.map(n => [n.dataset.id, +n.querySelector('rect').getAttribute('x')]))"
    )

    def x(label: str) -> float:
        return positions[_id(report, label)]

    assert x("reactive.calc total_revenue") > x("reactive.calc subtotal")
    assert x("reactive.calc total_revenue") > x("reactive.calc discount_multiplier")
    assert x("output result") > x("reactive.calc total_revenue")
    assert page.locator(".stage-label").count() == 0
    ranks = page.evaluate(
        "Object.fromEntries(dependencyRanks([{id:'a'}, {id:'b'}, {id:'c'}], [{from:'a',to:'b'}, {from:'b',to:'a'}, {from:'b',to:'c'}]))"
    )
    assert ranks["a"] == ranks["b"] < ranks["c"]


def test_module_toggle_preserves_boundary_edges(page: Page, tmp_path: Path) -> None:
    code = """from shiny import module, reactive, render

@module.server
def sales(input, output, session):
    @reactive.calc
    def total():
        return input.units()

    return total

def server(input, output, session):
    west = sales("west")
    east = sales("east")

    @render.text
    def combined():
        return str(west() + east())
"""
    report = _record(
        tmp_path, code, [{"west-units": 1, "east-units": 2, **_visible("combined")}]
    )
    combined = _id(report, "output combined")
    west_total = _node(report, "reactive.calc west:total")
    load_graph_report(page, format_reactlog_html(report, code))
    assert page.locator(".module-box").count() == 2
    page.locator('.module-box[data-module="west"] text').dblclick()
    expect(page.locator('.graph-node[data-id="module:west"]')).to_have_attribute(
        "aria-expanded", "false"
    )
    assert page.locator(west_total).count() == 0
    assert (
        page.locator(
            f'.graph-edge[data-from="module:west"][data-to="{combined}"]'
        ).count()
        == 1
    )
    assert page.locator(_node(report, "reactive.calc east:total")).count() == 1
    page.locator('.graph-node[data-id="module:west"]').dblclick()
    assert page.locator(west_total).count() == 1
    page.locator('.module-box[data-module="west"]').focus()
    page.keyboard.press("Enter")
    assert page.locator('.graph-node[data-id="module:west"]').count() == 1
    page.locator('.graph-node[data-id="module:west"]').focus()
    page.keyboard.press("Space")
    assert page.locator('.module-box[data-module="west"]').count() == 1


_CHART_CODE = """from shiny import render

def server(input, output, session):
    @render.plot
    def chart():
        input.n()
"""


def test_plot_preview_follows_timeline_without_future_images(
    page: Page, tmp_path: Path
) -> None:
    export = _export(tmp_path, _CHART_CODE, [{"n": 1, **_visible("chart")}])
    _add_plots(
        export, [("output chart", "First plot"), ("output chart", "Updated plot")]
    )
    report = load_reactlog_json(export)
    chart = _id(report, "output chart")
    steps = [i for i, e in enumerate(report["events"]) if e.get("plot")]
    load_graph_report(page, format_reactlog_html(report, _CHART_CODE))
    page.evaluate(f"selectNode('{chart}')")
    expect(page.locator("#insp-plot-image")).to_be_hidden()
    page.evaluate(f"seekTo({steps[0]})")
    expect(page.locator("#insp-plot-image")).to_be_visible()
    expect(page.locator("#insp-plot-image")).to_have_attribute("alt", "First plot")
    page.evaluate(f"seekTo({steps[1]})")
    expect(page.locator("#insp-plot-image")).to_have_attribute("alt", "Updated plot")
    page.evaluate(f"seekTo(0); selectNode('{chart}')")
    expect(page.locator("#insp-plot-image")).to_be_hidden()


def test_paused_video_seek_keeps_selected_plot_event(
    page: Page, tmp_path: Path
) -> None:
    code = """from shiny import render

def server(input, output, session):
    @render.plot
    def chart():
        input.n()

    @render.text
    def summary():
        return input.n()
"""
    report = _record(tmp_path, code, [{"n": 1, **_visible("chart", "summary")}])
    # `chart` and `summary` render within the same flush, so their timestamps
    # (nearly) coincide.
    step = _step(report, "enter", "output chart")
    load_graph_report(
        page, format_reactlog_html(report, code, video_path="recording.webm")
    )
    page.evaluate(
        f"seekTo({step}); document.getElementById('session-video').dispatchEvent(new Event('timeupdate'))"
    )
    expect(page.locator("#insp-title")).to_contain_text("output chart")
    page.evaluate(
        "document.getElementById('session-video').dispatchEvent(new Event('seeked'))"
    )
    expect(page.locator("#insp-title")).to_contain_text("output chart")


def test_imported_module_source_navigation(page: Page, tmp_path: Path) -> None:
    module_source = """from shiny import module, reactive

@module.server
def sales(input, output, session):
    @reactive.calc
    def revenue():
        return input.units() * 25

    return revenue
"""
    code = """from sales import sales
from shiny import render

def server(input, output, session):
    revenue = sales("west")

    @render.text
    def result():
        return str(revenue())
"""
    report = _record(
        tmp_path,
        code,
        [{"west-units": 1, **_visible("result")}],
        files={"sales.py": module_source},
    )
    revenue = _node(report, "reactive.calc west:revenue")
    load_graph_report(page, format_reactlog_html(report, code))
    page.locator(revenue).click()
    expect(page.locator("#insp-meta-line")).to_have_text("sales.py · Line 6")
    page.locator("#btn-toggle-source-drawer").click()
    expect(page.locator("#insp-source-code")).to_contain_text(
        "return input.units() * 25"
    )
    page.get_by_role("tab", name="App code").click()
    expect(page.get_by_label("Source file")).to_have_value("sales.py")
    expect(page.locator("#source-panel code")).to_contain_text(
        module_source.splitlines()[-1]
    )
    expect(page.locator("#source-panel .source-line.is-active")).to_contain_text(
        "def revenue():"
    )
    page.get_by_label("Source file").select_option("app.py")
    expect(page.locator("#source-panel code")).to_contain_text(
        "from sales import sales"
    )
    graph_node(page, _node(report, "output result")).click()
    expect(page.get_by_label("Source file")).to_have_value("app.py")
    expect(page.locator("#source-panel .source-line.is-active")).to_contain_text(
        "def result():"
    )
    page.evaluate("data => loadReactlogObject(data)", report)
    page.locator(revenue).click()
    expect(page.get_by_label("Source file")).to_have_value("sales.py")


def test_source_highlighting_survives_file_switches_and_json_import(
    page: Page, tmp_path: Path
) -> None:
    sources = {
        "app.py": "from shiny import reactive\n# A comment\n@reactive.calc\ndef amount():\n    return 25 + 2\n",
        "module.py": '"""Module docs\nMore docs <img src=x onerror=alert(1)>\n"""\ndef label():\n    return "Revenue"\n',
    }
    report = _record(tmp_path, _VAL_CODE, _VAL_STEPS)
    report.update(sources=sources, entry_file="app.py")
    load_graph_report(page, format_reactlog_html(report, sources["app.py"]))
    page.get_by_role("tab", name="App code").click()
    source = page.locator("#source-panel code")
    expect(source.locator(".syntax-keyword").first).to_have_text("from")
    expect(source.locator(".syntax-number").first).to_have_text("25")
    expect(source.locator(".syntax-comment")).to_have_text("# A comment")
    for theme in ("light", "dark"):
        page.locator("html").evaluate("(el, theme) => el.dataset.theme = theme", theme)
        assert source.locator(".syntax-keyword").first.evaluate(
            "(el) => getComputedStyle(el).color !== getComputedStyle(el.parentElement).color"
        )
    page.get_by_label("Source file").select_option("module.py")
    expect(source.locator(".source-line")).to_have_count(5)
    expect(source.locator('.source-line[data-line="2"] .syntax-string')).to_have_text(
        "More docs <img src=x onerror=alert(1)>"
    )
    expect(source.locator("img")).to_have_count(0)
    expect(source.locator('.source-line[data-line="4"] .syntax-keyword')).to_have_text(
        "def"
    )
    page.get_by_label("Source file").select_option("app.py")
    expect(source.locator(".syntax-keyword").first).to_have_text("from")
    # New source arriving through Open JSON must also be highlighted locally.
    replacement = dict(
        report,
        sources={"other.py": '# Imported\nvalue = "New file"\n'},
        entry_file="other.py",
    )
    page.evaluate("report => loadReactlogObject(report)", replacement)
    page.get_by_role("tab", name="App code").click()
    expect(source.locator(".syntax-comment")).to_have_text("# Imported")
    expect(source.locator(".syntax-string")).to_have_text('"New file"')


def test_inline_source_snippet_has_syntax_highlighting(
    page: Page, tmp_path: Path
) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def amount():
        return input.units() * 25

    @render.text
    def out():
        return str(amount())
"""
    report = _record(tmp_path, code, [{"units": 1, **_visible("out")}])
    load_graph_report(page, format_reactlog_html(report, code))
    graph_node(page, _node(report, "reactive.calc amount")).click()
    page.locator("#btn-toggle-source-drawer").click()
    snippet = page.locator("#insp-source-code")
    expect(snippet.locator(".syntax-keyword").first).to_have_text("def")
    expect(snippet.locator(".syntax-number")).to_have_text("25")
    expect(snippet.locator(".source-line.is-active")).to_contain_text("def amount():")


def test_reactlog_keyboard_navigation_and_shortcuts_modal(
    page: Page, tmp_path: Path
) -> None:
    code = """from shiny import render

def server(input, output, session):
    @render.text
    def out():
        return f"{input.x()}"
"""
    rlog = _record(tmp_path, code, [{"x": 1, **_visible("out")}, {"x": 2}])
    load_graph_report(page, format_reactlog_html(rlog, code))

    modal = page.locator("#shortcuts-modal")
    expect(modal).to_be_hidden()

    page.keyboard.press("?")
    expect(modal).to_be_visible()

    page.keyboard.press("Escape")
    expect(modal).to_be_hidden()

    scrubber = page.locator("#scrubber-range")
    init_val = int(scrubber.input_value())
    page.keyboard.press("ArrowRight")
    assert int(scrubber.input_value()) == init_val + 1


def test_reactlog_isolated_edge_styling(page: Page, tmp_path: Path) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def isolated_calc():
        with reactive.isolate():
            val = input.untracked()
        return val + input.tracked()

    @render.text
    def txt():
        return f"{isolated_calc()}"
"""
    rlog = _record(tmp_path, code, [{"untracked": 1, "tracked": 2, **_visible("txt")}])
    load_graph_report(page, format_reactlog_html(rlog, code))

    isolated_edges = page.locator(".graph-edge.is-isolated")
    expect(isolated_edges).to_have_count(1)
    expect(isolated_edges).to_have_attribute("stroke-dasharray", "5 4")
    expect(page.locator(".legend")).to_contain_text("Isolated read")


def test_isolated_reads_are_not_reported_as_causes(page: Page, tmp_path: Path) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @render.text
    def out():
        value = input.a()
        with reactive.isolate():
            value += input.b()
        return str(value)
"""
    report = _record(
        tmp_path, code, [{"a": 1, "b": 1, **_visible("out")}, {"b": 2}, {"a": 3}]
    )
    load_graph_report(page, format_reactlog_html(report, code))
    # Changing only the isolated `b` does not re-render `out`.
    page.evaluate(f"seekTo({_step(report, 'valueChange', 'input.b', 2)})")
    graph_node(page, _node(report, "output out")).click()
    expect(page.locator("#why-title")).to_contain_text("did not render")
    expect(page.locator("#insp-upstream-list")).not_to_contain_text("input.b")
    # The re-render after `a` changes.
    last_exit = max(
        i
        for i, e in enumerate(report["events"])
        if e["event"] == "exit" and e.get("node_label") == "output out"
    )
    page.evaluate(f"seekTo({last_exit})")
    expect(page.locator("#why-story")).to_contain_text("input.a")
    expect(page.locator("#why-story")).not_to_contain_text("input.b")
    expect(
        page.locator(f'.graph-edge.is-isolated[data-from="{_id(report, "input.b")}"]')
    ).to_have_count(1)


def test_reactlog_hotspot_badge(page: Page, tmp_path: Path) -> None:
    code = """from shiny import reactive, render

def server(input, output, session):
    @reactive.calc
    def compute():
        return input.val() * 2

    @render.text
    def txt():
        return f"{compute()}"
"""
    rlog = _record(
        tmp_path,
        code,
        [{"val": 1, **_visible("txt")}, {"val": 2}, {"val": 3}, {"val": 4}],
    )
    load_graph_report(page, format_reactlog_html(rlog, code))

    compute = _node(rlog, "reactive.calc compute")
    badge = page.locator(f"{compute} .node-exec-badge")
    expect(badge).to_be_visible()
    expect(badge).to_contain_text("4×")

    page.locator(compute).click()
    expect(page.locator("#insp-runs-badge")).to_contain_text("Runs: 4×")
    expect(page.locator("#insp-runs-badge svg.flame-icon")).not_to_be_attached()


def test_live_reactlog_input_and_mark_waves(page: Page, tmp_path: Path) -> None:
    code = """from shiny import reactive

def server(input, output, session):
    @reactive.effect
    def e():
        input.x()
"""
    export = _export(tmp_path, code, [{"x": 1}, {"x": 2}])
    # A bookmark set between the two recorded values of `x`.
    log = export["log"]
    change = next(
        i
        for i, e in enumerate(log)
        if e["action"] == "valueChange" and e.get("value") == "2"
    )
    log.insert(
        change,
        {"action": "userMark", "label": "checkpoint", "time": log[change]["time"]},
    )
    load_graph_report(
        page,
        format_reactlog_html(load_reactlog_json(export), source_code=code),
        wait_until="domcontentloaded",
    )

    expect(page.locator(".timeline-marker.is-mark")).to_have_count(1)
    report = load_reactlog_json(export)
    mark_step = next(
        i for i, event in enumerate(report["events"]) if event["event"] == "userMark"
    )
    page.locator("#scrubber-range").fill(str(mark_step))
    expect(page.locator("#active-flush-label")).to_contain_text("checkpoint")
    page.evaluate(f"seekTo({_step(report, 'valueChange', 'input.x', 2)})")
    expect(page.locator("#active-flush-label")).to_contain_text("x: 1 → 2")


def test_reactlog_flush_pipeline_and_stepper(page: Page, tmp_path: Path) -> None:
    data = _record(tmp_path, _VAL_CODE, [*_VAL_STEPS, {"val": 20}])
    load_graph_report(page, format_reactlog_html(data, _VAL_CODE))
    expect(page.locator("#flush-select, #flush-pipeline-bar")).to_have_count(0)
    page.locator("#btn-next-flush").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Flush 2")
    expect(page.locator("#flush-card")).to_be_visible()


def test_reactlog_overview_mode_and_module_cards(page: Page, tmp_path: Path) -> None:
    data = _record(tmp_path, _VAL_CODE, _VAL_STEPS)
    for node in data["nodes"]:
        node["module"] = "example"
    load_graph_report(page, format_reactlog_html(data, _VAL_CODE))
    page.locator("#btn-mode-overview").click()
    expect(page.locator(".module-card")).to_have_count(1)
    page.get_by_role("button", name="Zoom into Module").click()
    expect(page.locator("#module-overview-panel")).to_be_hidden()
    expect(page.locator(".graph-node")).to_have_count(len(data["nodes"]))


def test_reactlog_repeat_execution_badge_uniform(page: Page, tmp_path: Path) -> None:
    data = _record(tmp_path, _VAL_CODE, [*_VAL_STEPS, {"val": 20}, {"val": 30}])
    load_graph_report(page, format_reactlog_html(data, _VAL_CODE))
    badge = page.locator(_node(data, "output out") + " .node-exec-badge")
    expect(badge).to_be_visible()
    expect(badge).not_to_contain_text("🔥")
    expect(badge).to_contain_text("3")


def test_reactlog_inspector_drawer_toggle(page: Page, tmp_path: Path) -> None:
    data = _record(tmp_path, _VAL_CODE, _VAL_STEPS)
    load_graph_report(page, format_reactlog_html(data, _VAL_CODE))
    page.get_by_role("button", name="Close Inspector", exact=True).click()
    expect(page.locator("#sidebar")).to_be_hidden()
    page.get_by_role("button", name="Node details", exact=True).click()
    expect(page.locator("#sidebar")).to_be_visible()
