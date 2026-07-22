#!/usr/bin/env python3
"""Benchmark Pyright and Pyrefly and render a GitHub-friendly comparison."""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

Location = tuple[str, int, int]


@dataclass
class DiagnosticSummary:
    diagnostic_count: int
    diagnostic_files: int
    categories: dict[str, int]
    locations: set[Location]
    files_checked: int | None = None
    project_lines: int | None = None


@dataclass
class CheckerResult:
    name: str
    version: str
    exit_code: int
    durations: list[float]
    peak_memory_mib: float | None
    diagnostics: DiagnosticSummary

    @property
    def locations(self) -> set[Location]:
        return self.diagnostics.locations

    @classmethod
    def for_test(
        cls,
        *,
        name: str,
        durations: list[float],
        peak_memory_mib: float,
        locations: set[Location],
    ) -> CheckerResult:
        diagnostics = DiagnosticSummary(
            diagnostic_count=len(locations),
            diagnostic_files=len({location[0] for location in locations}),
            categories={},
            locations=locations,
        )
        return cls(name, "test", 0, durations, peak_memory_mib, diagnostics)


@dataclass
class CommandResult:
    exit_code: int
    duration: float
    peak_memory_mib: float | None
    stdout: str
    stderr: str


def _relative_path(path: str, repo_root: str) -> str:
    try:
        return os.path.relpath(path, repo_root)
    except ValueError:
        return path


def summarize_pyright(data: dict[str, Any], repo_root: str) -> DiagnosticSummary:
    diagnostics = data.get("generalDiagnostics", [])
    locations: set[Location] = set()
    categories: Counter[str] = Counter()
    files: set[str] = set()

    for diagnostic in diagnostics:
        path = _relative_path(diagnostic.get("file", "<unknown>"), repo_root)
        start = diagnostic.get("range", {}).get("start", {})
        # Pyright JSON uses zero-based lines and columns; Pyrefly uses one-based.
        location = (path, start.get("line", -1) + 1, start.get("character", -1) + 1)
        locations.add(location)
        files.add(path)
        categories[diagnostic.get("rule") or diagnostic.get("severity", "unknown")] += 1

    summary = data.get("summary", {})
    return DiagnosticSummary(
        diagnostic_count=len(diagnostics),
        diagnostic_files=len(files),
        categories=dict(categories),
        locations=locations,
        files_checked=summary.get("filesAnalyzed"),
    )


def summarize_pyrefly(data: dict[str, Any], stderr: str) -> DiagnosticSummary:
    diagnostics = data.get("errors", [])
    locations: set[Location] = set()
    categories: Counter[str] = Counter()
    files: set[str] = set()

    for diagnostic in diagnostics:
        path = diagnostic.get("path", "<unknown>")
        location = (path, diagnostic.get("line", -1), diagnostic.get("column", -1))
        locations.add(location)
        files.add(path)
        categories[diagnostic.get("name") or diagnostic.get("severity", "unknown")] += 1

    modules_match = re.search(r"([\d,]+) modules", stderr)
    lines_match = re.search(r"([\d,]+) lines in your project", stderr)
    return DiagnosticSummary(
        diagnostic_count=len(diagnostics),
        diagnostic_files=len(files),
        categories=dict(categories),
        locations=locations,
        files_checked=(
            int(modules_match.group(1).replace(",", "")) if modules_match else None
        ),
        project_lines=(
            int(lines_match.group(1).replace(",", "")) if lines_match else None
        ),
    )


def _run_command(command: Sequence[str], repo_root: Path) -> CommandResult:
    time_output = repo_root / ".type-checker-time.txt"
    wrapped_command = list(command)
    collect_memory = sys.platform.startswith("linux") and Path("/usr/bin/time").exists()
    if collect_memory:
        wrapped_command = [
            "/usr/bin/time",
            "-v",
            "-o",
            str(time_output),
            *wrapped_command,
        ]

    started = time.perf_counter()
    completed = subprocess.run(
        wrapped_command,
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    duration = time.perf_counter() - started

    peak_memory_mib = None
    if collect_memory:
        time_text = time_output.read_text()
        memory_match = re.search(
            r"Maximum resident set size \(kbytes\): (\d+)", time_text
        )
        if memory_match:
            peak_memory_mib = int(memory_match.group(1)) / 1024
        time_output.unlink(missing_ok=True)

    return CommandResult(
        completed.returncode,
        duration,
        peak_memory_mib,
        completed.stdout,
        completed.stderr,
    )


def _version(command: Sequence[str], repo_root: Path) -> str:
    completed = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.stdout.strip().splitlines()[0]


def benchmark_checker(
    *,
    name: str,
    command: Sequence[str],
    version_command: Sequence[str],
    runs: int,
    output_dir: Path,
    repo_root: Path,
) -> CheckerResult:
    command_results: list[CommandResult] = []
    for run_number in range(1, runs + 1):
        result = _run_command(command, repo_root)
        command_results.append(result)
        prefix = output_dir / f"{name.lower()}-run-{run_number}"
        prefix.with_suffix(".json").write_text(result.stdout)
        prefix.with_suffix(".stderr.txt").write_text(result.stderr)

    first = command_results[0]
    data = json.loads(first.stdout)
    diagnostics = (
        summarize_pyright(data, str(repo_root))
        if name == "Pyright"
        else summarize_pyrefly(data, first.stderr)
    )
    memory_values = [
        result.peak_memory_mib
        for result in command_results
        if result.peak_memory_mib is not None
    ]
    return CheckerResult(
        name=name,
        version=_version(version_command, repo_root),
        exit_code=first.exit_code,
        durations=[result.duration for result in command_results],
        peak_memory_mib=max(memory_values) if memory_values else None,
        diagnostics=diagnostics,
    )


def _format_optional(value: int | float | None, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.1f}{suffix}"
    return f"{value:,}{suffix}"


def _top_categories(result: CheckerResult) -> str:
    categories = sorted(
        result.diagnostics.categories.items(), key=lambda item: (-item[1], item[0])
    )[:10]
    return ", ".join(f"`{name}` ({count})" for name, count in categories) or "none"


def build_report(pyright: CheckerResult, pyrefly: CheckerResult, runs: int) -> str:
    pyright_median = statistics.median(pyright.durations)
    pyrefly_median = statistics.median(pyrefly.durations)
    savings = (1 - pyrefly_median / pyright_median) * 100
    speedup = pyright_median / pyrefly_median
    overlap = len(pyright.locations & pyrefly.locations)

    if savings >= 0:
        headline = f"**{savings:.1f}% less checker time** (**{speedup:.2f}x faster**)"
    else:
        headline = (
            f"**{-savings:.1f}% more checker time** (**{1 / speedup:.2f}x slower**)"
        )

    lines = [
        "# Pyright vs Pyrefly",
        "",
        f"Across {runs} runs, Pyrefly used {headline} by median wall-clock time.",
        "",
        "| Criterion | Pyright | Pyrefly |",
        "| --- | ---: | ---: |",
        f"| Version | `{pyright.version}` | `{pyrefly.version}` |",
        f"| Exit code | {pyright.exit_code} | {pyrefly.exit_code} |",
        f"| Median wall time | {pyright_median:.2f}s | {pyrefly_median:.2f}s |",
        f"| Best wall time | {min(pyright.durations):.2f}s | {min(pyrefly.durations):.2f}s |",
        "| Peak RSS (highest run) | "
        f"{_format_optional(pyright.peak_memory_mib, ' MiB')} | "
        f"{_format_optional(pyrefly.peak_memory_mib, ' MiB')} |",
        f"| Diagnostics | {pyright.diagnostics.diagnostic_count:,} | {pyrefly.diagnostics.diagnostic_count:,} |",
        f"| Files with diagnostics | {pyright.diagnostics.diagnostic_files:,} | {pyrefly.diagnostics.diagnostic_files:,} |",
        "| Files/modules analyzed | "
        f"{_format_optional(pyright.diagnostics.files_checked)} | "
        f"{_format_optional(pyrefly.diagnostics.files_checked)} |",
        "| Project lines reported | "
        f"{_format_optional(pyright.diagnostics.project_lines)} | "
        f"{_format_optional(pyrefly.diagnostics.project_lines)} |",
        f"| Exact diagnostic-location overlap | {overlap} | {overlap} |",
        "",
        f"**Pyright top diagnostic rules:** {_top_categories(pyright)}",
        "",
        f"**Pyrefly top diagnostic kinds:** {_top_categories(pyrefly)}",
        "",
        "> Wall time includes process startup and uses the median to reduce noise. Peak RSS is measured by GNU `time` on Linux. Files and modules are checker-specific units, so treat that row as context rather than exact coverage parity. Full JSON and stderr outputs are attached as the `type-checker-comparison` artifact.",
        "",
    ]
    return "\n".join(lines)


def _metrics(result: CheckerResult) -> dict[str, Any]:
    return {
        "name": result.name,
        "version": result.version,
        "exit_code": result.exit_code,
        "durations_seconds": result.durations,
        "median_seconds": statistics.median(result.durations),
        "peak_memory_mib": result.peak_memory_mib,
        "diagnostics": result.diagnostics.diagnostic_count,
        "diagnostic_files": result.diagnostics.diagnostic_files,
        "files_checked": result.diagnostics.files_checked,
        "project_lines": result.diagnostics.project_lines,
        "categories": result.diagnostics.categories,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, default=Path("type-checker-results"))
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be at least 1")

    repo_root = Path(__file__).resolve().parents[1]
    output_dir = (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    pyright = benchmark_checker(
        name="Pyright",
        command=["pyright", "--outputjson"],
        version_command=["pyright", "--version"],
        runs=args.runs,
        output_dir=output_dir,
        repo_root=repo_root,
    )
    pyrefly = benchmark_checker(
        name="Pyrefly",
        command=[
            "pyrefly",
            "check",
            "--output-format=json",
            "--summary=full",
            "--progress-bar=no",
        ],
        version_command=["pyrefly", "--version"],
        runs=args.runs,
        output_dir=output_dir,
        repo_root=repo_root,
    )

    report = build_report(pyright, pyrefly, args.runs)
    (output_dir / "summary.md").write_text(report)
    (output_dir / "metrics.json").write_text(
        json.dumps(
            {"pyright": _metrics(pyright), "pyrefly": _metrics(pyrefly)},
            indent=2,
        )
        + "\n"
    )
    print(report)

    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a") as summary_file:
            summary_file.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
