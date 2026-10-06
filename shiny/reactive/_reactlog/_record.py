from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, cast

from ...run._run import run_shiny_app


def _record_session_sync(
    app_path: str,
    video_path: Optional[str] = "recording.webm",
    headless: bool = False,
    record_script: Optional[Callable[[Any], None]] = None,
    timeout_secs: float = 60.0,
    auto_interact: bool = False,
    redact_inputs: bool = False,
    viewport_size: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {
            "success": False,
            "error": "Playwright is not installed. Install it with: pip install playwright && playwright install chromium",
            "actions": [],
            "video_path": None,
        }

    app_target = Path(app_path).resolve()
    if not app_target.exists():
        return {
            "success": False,
            "error": f"App file not found: {app_path}",
            "actions": [],
            "video_path": None,
        }

    start_time = time.time()
    try:
        sa = run_shiny_app(
            app_target,
            wait_for_start=True,
            timeout_secs=min(timeout_secs, 30.0),
            env={"SHINY_TESTMODE": "1", "PYTHONUNBUFFERED": "1", "SHINY_REACTLOG": "1"},
        )
    except Exception as err:
        return {
            "success": False,
            "error": f"Failed to start Shiny app: {err}",
            "actions": [],
            "video_path": None,
        }

    app_url = sa.url
    temp_dir = tempfile.mkdtemp(prefix="shiny_record_")
    recorded_actions: List[Dict[str, Any]] = []
    saved_video_path: Optional[str] = None

    try:
        with sync_playwright() as p:
            ws_endpoint = os.environ.get("PW_TEST_CONNECT_WS_ENDPOINT")
            if ws_endpoint:
                connect_kwargs: Dict[str, Any] = {}
                connect_param_name = (
                    "endpoint"
                    if "endpoint" in inspect.signature(p.chromium.connect).parameters
                    else "ws_endpoint"
                )
                connect_kwargs[connect_param_name] = ws_endpoint
                expose_net = os.environ.get("PW_TEST_CONNECT_EXPOSE_NETWORK")
                if expose_net:
                    connect_kwargs["expose_network"] = expose_net
                browser = p.chromium.connect(**connect_kwargs)
            else:
                browser = p.chromium.launch(headless=headless)
            v_width = (
                int(viewport_size["width"])
                if viewport_size and "width" in viewport_size
                else 1280
            )
            v_height = (
                int(viewport_size["height"])
                if viewport_size and "height" in viewport_size
                else 1440
            )
            context = browser.new_context(
                record_video_dir=temp_dir,
                record_video_size={"width": v_width, "height": v_height},
                viewport={"width": v_width, "height": v_height},
            )
            page = context.new_page()
            page_start_time = time.time()

            redact_all_js = "true" if redact_inputs else "false"
            recorder_init_script = f"""
            window.__recordedActions = [];
            window.__recordStartTime = Date.now();
            const recentInputs = new Map();
            let lastClickTime = 0;
            let lastClickTarget = '';
            const shouldRedactAll = {redact_all_js};

            function isSensitiveInput(name, el) {{
                if (shouldRedactAll) return true;
                if (el && (el.type === 'password' || el.getAttribute('type') === 'password')) return true;
                const lower = (name || '').toLowerCase();
                return lower.includes('password') || lower.includes('secret') || lower.includes('token') || lower.includes('api_key') || lower.includes('apikey');
            }}

            function trackAction(item) {{
                item.timestamp = Date.now() - window.__recordStartTime;
                window.__recordedActions.push(item);
            }}

            function attachShinyListeners() {{
                if (window.$ && window.Shiny) {{
                    $(document).off('.shinyRecorder');
                    $(document).on('shiny:inputchanged.shinyRecorder', (e) => {{
                        if (e.name.startsWith('.')) return;
                        const el = document.getElementById(e.name) || document.querySelector('[name="' + e.name + '"]');
                        const sensitive = isSensitiveInput(e.name, el);
                        const safeVal = sensitive ? '[REDACTED]' : e.value;
                        const valKey = typeof safeVal === 'object' ? JSON.stringify(safeVal) : String(safeVal);
                        recentInputs.set(e.name, {{ val: valKey, t: Date.now() }});
                        trackAction({{
                            type: 'input',
                            name: e.name,
                            value: safeVal,
                            inputType: e.inputType || 'shiny'
                        }});
                    }});
                    $(document).on('shiny:value.shinyRecorder', (e) => {{
                        trackAction({{
                            type: 'output',
                            name: e.name,
                            plot: e.value && typeof e.value.src === 'string' && /^data:image\\/(png|jpeg|gif|webp);base64,/.test(e.value.src)
                                ? {{ src: e.value.src, alt: e.value.alt || e.name }} : undefined
                        }});
                    }});
                }}
            }}

            document.addEventListener('DOMContentLoaded', attachShinyListeners);
            window.addEventListener('load', attachShinyListeners);
            document.addEventListener('shiny:connected', attachShinyListeners);

            document.addEventListener('change', (e) => {{
                const target = e.target;
                if (!target || !target.id || target.id.startsWith('.')) return;
                const id = target.id;
                const sensitive = isSensitiveInput(id, target);
                const rawVal = target.value !== undefined ? target.value : target.checked;
                const val = sensitive ? '[REDACTED]' : rawVal;
                const valKey = String(val);
                const rec = recentInputs.get(id);
                if (rec && (Date.now() - rec.t < 350) && rec.val === valKey) {{
                    return;
                }}
                if (window.Shiny && window.Shiny.setInputValue && target.closest('.shiny-input-container')) {{
                    return;
                }}
                recentInputs.set(id, {{ val: valKey, t: Date.now() }});
                trackAction({{
                    type: 'input',
                    name: id,
                    value: val,
                    inputType: target.type || target.tagName.toLowerCase()
                }});
            }}, true);

            document.addEventListener('click', (e) => {{
                const target = e.target.closest('button, input, select, textarea, a, .btn');
                if (!target) return;
                const tgtName = target.id || target.name || target.tagName.toLowerCase();
                const now = Date.now();
                if (tgtName === lastClickTarget && (now - lastClickTime < 200)) {{
                    return;
                }}
                lastClickTime = now;
                lastClickTarget = tgtName;
                trackAction({{
                    type: 'click',
                    target: tgtName,
                    text: (target.innerText || target.value || '').trim().slice(0, 50)
                }});
            }}, true);
            """
            page.add_init_script(recorder_init_script)

            page.goto(app_url, wait_until="domcontentloaded")
            time.sleep(0.5)

            if record_script:
                record_script(page)
                time.sleep(0.5)
            elif not headless:
                try:
                    sys.stderr.write(
                        "\n🔴 Recording browser session... Interact with your Shiny app.\n"
                        "Press [Enter] here (or close the browser window) when done recording: "
                    )
                    sys.stderr.flush()
                    deadline = time.time() + timeout_secs
                    while time.time() < deadline:
                        if page.is_closed():
                            break
                        import select

                        empty_r: List[Any] = []
                        empty_w: List[Any] = []
                        r, _, _ = select.select([sys.stdin], empty_r, empty_w, 0.3)
                        if r:
                            sys.stdin.readline()
                            break
                except Exception:
                    time.sleep(2.0)
            elif auto_interact:
                try:
                    time.sleep(0.8)
                    input_locators = page.locator(
                        "input.shiny-input-number, input.shiny-input-text, input[type='number'], input[type='text']"
                    ).all()
                    for inp in input_locators[:3]:
                        try:
                            val = inp.input_value()
                            if val.isdigit():
                                inp.fill(str(int(val) + 5))
                            elif val:
                                inp.fill(f"{val} Updated")
                            time.sleep(0.4)
                        except Exception:
                            pass

                    buttons = page.locator(
                        "button.action-button, button.btn-primary, button.btn"
                    ).all()
                    for btn in buttons[:2]:
                        try:
                            btn.click()
                            time.sleep(0.5)
                        except Exception:
                            pass
                except Exception:
                    time.sleep(1.0)
            else:
                time.sleep(1.0)

            try:
                if not page.is_closed():
                    raw_actions = page.evaluate("() => window.__recordedActions || []")
                    if isinstance(raw_actions, list):
                        recorded_actions = cast(List[Dict[str, Any]], raw_actions)
            except Exception:
                pass

            app_marks: List[Dict[str, Any]] = []
            try:
                import urllib.request

                req = urllib.request.Request(f"{app_url.rstrip('/')}/__reactlog__/mark")
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    mark_data = json.loads(resp.read().decode())
                    if isinstance(mark_data, dict) and "marks" in mark_data:
                        raw_marks = cast(List[Dict[str, Any]], mark_data["marks"])
                        for rm in raw_marks:
                            item = dict(rm)
                            raw_t = float(item.get("time") or 0.0)
                            if raw_t > 1_000_000_000:
                                rel_sec = max(0.0, round(raw_t - page_start_time, 2))
                                item["time"] = rel_sec
                                item["timestamp"] = int(rel_sec * 1000)
                            app_marks.append(item)
            except Exception:
                pass

            page_video = page.video

            page.close()
            context.close()

            if page_video and video_path:
                out_v = Path(video_path).resolve()
                out_v.parent.mkdir(parents=True, exist_ok=True)
                try:
                    page_video.save_as(str(out_v))
                    saved_video_path = str(out_v)
                except Exception:
                    pass
            elif page_video:
                temp_video = Path(temp_dir) / "recording.webm"
                try:
                    page_video.save_as(str(temp_video))
                    saved_video_path = str(temp_video)
                except Exception:
                    pass

            browser.close()

        if not saved_video_path:
            video_files = list(Path(temp_dir).glob("*.webm"))
            if video_files and video_path:
                out_v = Path(video_path).resolve()
                out_v.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(video_files[0], out_v)
                saved_video_path = str(out_v)
            elif video_files:
                saved_video_path = str(video_files[0])

        if not app_marks:
            try:
                import urllib.request

                req = urllib.request.Request(f"{app_url.rstrip('/')}/__reactlog__/mark")
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    mark_data = json.loads(resp.read().decode())
                    if isinstance(mark_data, dict) and "marks" in mark_data:
                        raw_marks = cast(List[Dict[str, Any]], mark_data["marks"])
                        for rm in raw_marks:
                            item = dict(rm)
                            raw_t = float(item.get("time") or 0.0)
                            if raw_t > 1_000_000_000:
                                rel_sec = max(0.0, round(raw_t - page_start_time, 2))
                                item["time"] = rel_sec
                                item["timestamp"] = int(rel_sec * 1000)
                            app_marks.append(item)
            except Exception:
                pass

        return {
            "success": True,
            "actions": recorded_actions,
            "marks": app_marks,
            "video_path": saved_video_path,
            "duration_secs": round(time.time() - start_time, 2),
        }

    finally:
        sa.close()
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


def record_shiny_session(
    app_path: str,
    video_path: Optional[str] = "recording.webm",
    headless: bool = False,
    record_script: Optional[Callable[[Any], None]] = None,
    timeout_secs: float = 60.0,
    auto_interact: bool = False,
    redact_inputs: bool = False,
    viewport_size: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    try:
        asyncio.get_running_loop()
        has_running_loop = True
    except RuntimeError:
        has_running_loop = False

    if has_running_loop:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                _record_session_sync,
                app_path,
                video_path,
                headless,
                record_script,
                timeout_secs,
                auto_interact,
                redact_inputs,
                viewport_size,
            )
            return future.result()
    return _record_session_sync(
        app_path,
        video_path,
        headless,
        record_script,
        timeout_secs,
        auto_interact,
        redact_inputs,
        viewport_size,
    )
