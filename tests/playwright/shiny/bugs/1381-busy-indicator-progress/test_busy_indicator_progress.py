"""
Each output's "recalculating" message must reach the browser while the output
renders, so that its busy indicator shows. In #1381, on Windows, the messages for
most outputs arrived together with the finished values.
"""

import json
from typing import cast

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc

OUTPUTS = ["out1", "out2", "out3", "out4"]
# Each output blocks the event loop for 0.5 s while it renders (see app.py).
MIN_GAP_MS = 250

# Records when the browser receives each websocket message.
RECORD_MESSAGES = """
window.__shinyMessages = [];
window.WebSocket = class extends window.WebSocket {
  constructor(...args) {
    super(...args);
    this.addEventListener("message", (e) => {
      window.__shinyMessages.push([performance.now(), e.data]);
    });
  }
};
"""


def status_times(page: Page) -> dict[tuple[str, str], float]:
    """The first time that each (output, status) message was received, in ms."""
    times: dict[tuple[str, str], float] = {}
    messages: list[tuple[float, object]] = page.evaluate("window.__shinyMessages")
    for t, data in messages:
        if not isinstance(data, str):
            continue
        try:
            msg: object = json.loads(data)
        except ValueError:
            continue
        if not isinstance(msg, dict):
            continue
        recalc = cast("dict[str, object]", msg).get("recalculating")
        if isinstance(recalc, dict):
            status = cast("dict[str, str]", recalc)
            times.setdefault((status["name"], status["status"]), t)
    return times


def test_recalculating_messages_arrive_while_outputs_render(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.add_init_script(RECORD_MESSAGES)
    page.goto(local_app.url)
    controller.OutputText(page, "out4").expect_value("0", timeout=10_000)

    page.evaluate("window.__shinyMessages = []")
    controller.InputActionButton(page, "rerender").click()
    controller.OutputText(page, "out4").expect_value("1", timeout=10_000)

    times = status_times(page)
    gaps = {
        name: times[(name, "recalculated")] - times[(name, "recalculating")]
        for name in OUTPUTS
    }
    print("ms between recalculating and recalculated:", gaps)
    assert all(gap >= MIN_GAP_MS for gap in gaps.values()), gaps
