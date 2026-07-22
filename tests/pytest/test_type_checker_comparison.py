from scripts.compare_type_checkers import (
    CheckerResult,
    build_report,
    summarize_pyrefly,
    summarize_pyright,
)


def test_summarize_pyright_normalizes_zero_based_locations() -> None:
    summary = summarize_pyright(
        {
            "generalDiagnostics": [
                {
                    "file": "/repo/shiny/app.py",
                    "severity": "error",
                    "rule": "reportArgumentType",
                    "range": {"start": {"line": 2, "character": 4}},
                }
            ],
            "summary": {"filesAnalyzed": 42},
        },
        repo_root="/repo",
    )

    assert summary.diagnostic_count == 1
    assert summary.files_checked == 42
    assert summary.categories == {"reportArgumentType": 1}
    assert summary.locations == {("shiny/app.py", 3, 5)}


def test_summarize_pyrefly_uses_one_based_locations() -> None:
    summary = summarize_pyrefly(
        {
            "errors": [
                {
                    "path": "shiny/app.py",
                    "line": 3,
                    "column": 5,
                    "name": "bad-argument-type",
                    "severity": "error",
                }
            ]
        },
        stderr=(
            "INFO 1,184 modules (2,717 dependent modules); "
            "1,581,188 lines (124,791 lines in your project)"
        ),
    )

    assert summary.diagnostic_count == 1
    assert summary.files_checked == 1184
    assert summary.project_lines == 124791
    assert summary.categories == {"bad-argument-type": 1}
    assert summary.locations == {("shiny/app.py", 3, 5)}


def test_build_report_calculates_median_savings_and_location_overlap() -> None:
    pyright = CheckerResult.for_test(
        name="Pyright",
        durations=[12.0, 10.0, 11.0],
        peak_memory_mib=1000.0,
        locations={("a.py", 1, 1), ("b.py", 2, 2)},
    )
    pyrefly = CheckerResult.for_test(
        name="Pyrefly",
        durations=[2.0, 1.0, 1.5],
        peak_memory_mib=700.0,
        locations={("b.py", 2, 2), ("c.py", 3, 3)},
    )

    report = build_report(pyright, pyrefly, runs=3)

    assert "**86.4% less checker time**" in report
    assert "**7.33x faster**" in report
    assert "Exact diagnostic-location overlap | 1" in report
