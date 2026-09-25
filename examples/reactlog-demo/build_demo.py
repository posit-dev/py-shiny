"""Record the app and export a self-contained report into dist/.

Run from the repository root: python examples/reactlog-demo/build_demo.py
Requires the local Shiny checkout, matplotlib, and Playwright Chromium.
"""

import json
import shutil
from pathlib import Path

from shiny._inspect import format_reactlog_html, generate_reactlog, record_shiny_session

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"


def interact(page):
    page.locator("#baseline-revenue_plot img").wait_for()
    page.locator("#portfolio_plot img").wait_for()
    page.wait_for_timeout(800)
    page.locator("#campaign-units").fill("240")
    page.locator("#campaign-units").press("Tab")
    page.wait_for_timeout(1000)
    page.locator("#campaign-apply_discount").click()
    page.wait_for_timeout(1000)
    page.locator("#campaign-cost").fill("28")
    page.locator("#campaign-cost").press("Tab")
    page.wait_for_timeout(1000)
    page.locator("#fixed_cost").fill("2400")
    page.locator("#fixed_cost").press("Tab")
    page.wait_for_timeout(1000)
    page.locator("#target").fill("40000")
    page.locator("#target").press("Tab")
    page.wait_for_timeout(1000)
    page.locator("#baseline-price").fill("49")
    page.locator("#baseline-price").press("Tab")
    page.wait_for_timeout(1200)


def main():
    DIST.mkdir(exist_ok=True)
    for name in ("app.py", "scenario.py"):
        shutil.copyfile(Path(__file__).with_name(name), DIST / name)
    result = record_shiny_session(
        str(DIST / "app.py"),
        video_path=str(DIST / "recording.webm"),
        headless=True,
        record_script=interact,
    )
    if not result.get("success"):
        raise RuntimeError(result)
    actions = result["actions"]
    source = (DIST / "app.py").read_text()
    report = generate_reactlog(
        source,
        recorded_actions=actions,
        video_path="recording.webm",
        source_path=DIST / "app.py",
    )
    (DIST / "recording-actions.json").write_text(json.dumps(actions, indent=2))
    (DIST / "reactlog.json").write_text(json.dumps(report, indent=2))
    (DIST / "index.html").write_text(
        format_reactlog_html(
            report,
            source,
            title="Northstar · Reactlog report",
            html_path=str(DIST / "index.html"),
            video_path=str(DIST / "recording.webm"),
            theme="light",
        )
    )
    shutil.copyfile(Path(__file__).with_name("README.md"), DIST / "README.md")
    print(
        f"Built {DIST}: {len(report['nodes'])} nodes, {len(report['edges'])} edges, {sum('plot' in e for e in report['events'])} plot snapshots"
    )


if __name__ == "__main__":
    main()
