"""Measure startup scenarios for `import shiny` on a given interpreter.

Each scenario runs in a fresh subprocess `--runs` times; we report the min and
median wall-clock time in milliseconds. Interpreter startup (~25-40ms) is
included, since that is what users actually pay per process (dev reloads, CLI,
test workers).

Usage:
    python benchmark_startup.py [--python /path/to/python] [--runs 10]
"""

import argparse
import statistics
import subprocess
import sys
import time

SCENARIOS = {
    "interpreter only": "pass",
    "import shiny": "import shiny",
    "from shiny import App, ui": "from shiny import App, ui",
    "app boot (App + page)": (
        "from shiny import App, ui\n" "app = App(ui.page_fluid(ui.h1('hi')), None)"
    ),
}


def time_scenario(python: str, code: str, runs: int) -> tuple[float, float]:
    times: list[float] = []
    for _ in range(runs):
        start = time.perf_counter()
        result = subprocess.run([python, "-c", code], capture_output=True, text=True)
        elapsed_ms = (time.perf_counter() - start) * 1000
        if result.returncode != 0:
            raise RuntimeError(
                f"Scenario failed on {python!r}: {code!r}\n{result.stderr}"
            )
        times.append(elapsed_ms)
    return min(times), statistics.median(times)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--runs", type=int, default=10)
    args = parser.parse_args()

    print(f"python: {args.python} (runs: {args.runs})")
    print(f"{'scenario':<26} {'min':>9} {'median':>9}")
    for label, code in SCENARIOS.items():
        fastest, median = time_scenario(args.python, code, args.runs)
        print(f"{label:<26} {fastest:>7.0f}ms {median:>7.0f}ms")


if __name__ == "__main__":
    main()
