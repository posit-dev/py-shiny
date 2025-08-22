"""
Script to average inspect-ai and pytest results across multiple attempts.

This script processes results from multiple attempts stored in separate directories
and creates averaged results maintaining the same structure as single-attempt results.
"""

import json
import statistics
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Union


def process_inspect_ai_results(attempts_dir: Path) -> Dict[str, Any]:
    """
    Process and average inspect-ai results across multiple attempts.

    Args:
        attempts_dir: Directory containing attempt subdirectories

    Returns:
        Averaged summary dictionary with same structure as single attempt
    """
    attempt_dirs = [
        d
        for d in attempts_dir.iterdir()
        if d.is_dir() and d.name.startswith("attempt_")
    ]
    attempt_dirs.sort(key=lambda x: int(x.name.split("_")[1]))

    if not attempt_dirs:
        print("No attempt directories found")
        return {}

    print(f"Found {len(attempt_dirs)} attempts to average")

    all_summaries: List[Dict[str, Union[int, float, bool]]] = []

    for attempt_dir in attempt_dirs:
        # Find the JSON result file in this attempt
        json_files = list(attempt_dir.glob("*.json"))
        if not json_files:
            print(f"Warning: No JSON files found in {attempt_dir}")
            continue

        # Use the first JSON file (should only be one)
        result_file = json_files[0]

        # Process this single result to get summary
        with open(result_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {result_file}: {e}")
                continue

        samples = data.get("samples", [])
        total_tests = len(samples)

        if total_tests == 0:
            print(f"Warning: No samples found in {result_file}")
            continue

        # Count results
        passed_tests = sum(
            1
            for s in samples
            if s.get("scores", {}).get("model_graded_qa", {}).get("value") == "C"
        )
        partial_tests = sum(
            1
            for s in samples
            if s.get("scores", {}).get("model_graded_qa", {}).get("value") == "P"
        )
        failed_tests = sum(
            1
            for s in samples
            if s.get("scores", {}).get("model_graded_qa", {}).get("value") == "I"
        )

        passing_tests = passed_tests + partial_tests
        pass_rate = (passing_tests / total_tests) * 100 if total_tests > 0 else 0

        summary: Dict[str, Union[int, float, bool]] = {
            "total": total_tests,
            "passed": passed_tests,
            "partial": partial_tests,
            "failed": failed_tests,
            "pass_rate": pass_rate,
            "quality_gate_passed": pass_rate >= 80,
        }

        all_summaries.append(summary)
        print(
            f"Attempt {attempt_dir.name}: {passed_tests}C + {partial_tests}P + {failed_tests}I = {passing_tests}/{total_tests} ({pass_rate:.1f}%)"
        )

    if not all_summaries:
        print("No valid summaries found to average")
        return {}

    # Calculate averages
    avg_summary: Dict[str, Union[int, float, bool, str]] = {
        "total": statistics.mean(float(s["total"]) for s in all_summaries),
        "passed": statistics.mean(float(s["passed"]) for s in all_summaries),
        "partial": statistics.mean(float(s["partial"]) for s in all_summaries),
        "failed": statistics.mean(float(s["failed"]) for s in all_summaries),
        "pass_rate": statistics.mean(float(s["pass_rate"]) for s in all_summaries),
    }

    # Round to reasonable precision
    avg_summary["total"] = round(float(avg_summary["total"]), 1)
    avg_summary["passed"] = round(float(avg_summary["passed"]), 1)
    avg_summary["partial"] = round(float(avg_summary["partial"]), 1)
    avg_summary["failed"] = round(float(avg_summary["failed"]), 1)
    avg_summary["pass_rate"] = round(float(avg_summary["pass_rate"]), 1)
    avg_summary["quality_gate_passed"] = avg_summary["pass_rate"] >= 80
    avg_summary["details"] = (
        f"Averaged across {len(all_summaries)} attempts: "
        f"Complete: {avg_summary['passed']}, Partial: {avg_summary['partial']}, "
        f"Incomplete: {avg_summary['failed']}, "
        f"Passing: {avg_summary['passed'] + avg_summary['partial']}/{avg_summary['total']}"
    )

    return avg_summary


def process_pytest_results(attempts_dir: Path) -> Dict[str, Any]:
    """
    Process and average pytest results across multiple attempts.

    Args:
        attempts_dir: Directory containing attempt subdirectories

    Returns:
        Averaged pytest summary dictionary
    """
    attempt_dirs = [
        d
        for d in attempts_dir.iterdir()
        if d.is_dir() and d.name.startswith("attempt_")
    ]
    attempt_dirs.sort(key=lambda x: int(x.name.split("_")[1]))

    if not attempt_dirs:
        print("No attempt directories found for pytest results")
        return {}

    all_pytest_summaries: List[Dict[str, Union[int, float]]] = []

    for attempt_dir in attempt_dirs:
        xml_file = attempt_dir / "test-results.xml"
        if not xml_file.exists():
            print(f"Warning: No test-results.xml found in {attempt_dir}")
            continue

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Extract test metrics from XML
            total_tests = int(root.get("tests", 0))
            failures = int(root.get("failures", 0))
            errors = int(root.get("errors", 0))
            skipped = int(root.get("skipped", 0))

            passed_tests = total_tests - failures - errors - skipped
            pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

            pytest_summary: Dict[str, Union[int, float]] = {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failures,
                "errors": errors,
                "skipped": skipped,
                "pass_rate": pass_rate,
            }

            all_pytest_summaries.append(pytest_summary)
            print(
                f"Attempt {attempt_dir.name} pytest: {passed_tests}/{total_tests} passed ({pass_rate:.1f}%)"
            )

        except (ET.ParseError, ValueError) as e:
            print(f"Error parsing {xml_file}: {e}")
            continue

    if not all_pytest_summaries:
        print("No valid pytest summaries found to average")
        return {}

    # Calculate averages for pytest
    avg_pytest: Dict[str, Union[int, float, str]] = {
        "total": statistics.mean(float(s["total"]) for s in all_pytest_summaries),
        "passed": statistics.mean(float(s["passed"]) for s in all_pytest_summaries),
        "failed": statistics.mean(float(s["failed"]) for s in all_pytest_summaries),
        "errors": statistics.mean(float(s["errors"]) for s in all_pytest_summaries),
        "skipped": statistics.mean(float(s["skipped"]) for s in all_pytest_summaries),
        "pass_rate": statistics.mean(
            float(s["pass_rate"]) for s in all_pytest_summaries
        ),
    }

    # Round to reasonable precision
    for key in avg_pytest:
        if key != "details":
            avg_pytest[key] = round(float(avg_pytest[key]), 1)

    avg_pytest["details"] = (
        f"Averaged across {len(all_pytest_summaries)} attempts: "
        f"Passed: {avg_pytest['passed']}, Failed: {avg_pytest['failed']}, "
        f"Errors: {avg_pytest['errors']}, Skipped: {avg_pytest['skipped']} "
        f"({avg_pytest['pass_rate']:.1f}% pass rate)"
    )

    return avg_pytest


def main():
    """Main function to process and average results."""
    if len(sys.argv) != 3:
        print("Usage: python average_results.py <attempts_dir> <output_dir>")
        sys.exit(1)

    attempts_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not attempts_dir.exists() or not attempts_dir.is_dir():
        print(f"Error: Attempts directory does not exist: {attempts_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Process inspect-ai results
    print("Processing inspect-ai results...")
    inspect_summary = process_inspect_ai_results(attempts_dir)

    if inspect_summary:
        summary_file = output_dir / "summary.json"
        with open(summary_file, "w") as f:
            json.dump(inspect_summary, f, indent=2)
        print(f"Inspect-AI averaged summary saved to: {summary_file}")
        print(
            f"Averaged pass rate (Complete + Partial): {inspect_summary['pass_rate']:.1f}%"
        )
    else:
        print("No inspect-ai results to average")

    # Process pytest results
    print("\nProcessing pytest results...")
    pytest_summary = process_pytest_results(attempts_dir)

    if pytest_summary:
        pytest_summary_file = output_dir / "pytest_summary.json"
        with open(pytest_summary_file, "w") as f:
            json.dump(pytest_summary, f, indent=2)
        print(f"Pytest averaged summary saved to: {pytest_summary_file}")
        print(f"Averaged pytest pass rate: {pytest_summary['pass_rate']:.1f}%")
    else:
        print("No pytest results to average")

    # Create a combined summary
    if inspect_summary or pytest_summary:
        combined_summary = {
            "inspect_ai": inspect_summary,
            "pytest": pytest_summary,
            "overall_quality_gate_passed": (
                (
                    inspect_summary.get("quality_gate_passed", False)
                    and (
                        pytest_summary.get("pass_rate", 0) >= 85
                    )  # 85% threshold for pytest
                )
                if inspect_summary and pytest_summary
                else False
            ),
        }

        combined_file = output_dir / "combined_summary.json"
        with open(combined_file, "w") as f:
            json.dump(combined_summary, f, indent=2)
        print(f"Combined summary saved to: {combined_file}")


if __name__ == "__main__":
    main()
