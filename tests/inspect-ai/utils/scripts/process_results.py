import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Union


def process_inspect_results(result_file_path: Union[str, Path]) -> None:
    """Process a single Inspect AI result file and generate a summary."""
    input_path = Path(result_file_path)

    # 1. Validate that the input path is a valid .json file
    if not input_path.is_file() or input_path.suffix.lower() != ".json":
        print(f"Error: The provided path is not a valid .json file: {input_path}")
        sys.exit(1)

    print(f"Processing file: {input_path.name}")

    # 2. Load the JSON data with error handling
    with open(input_path, "r", encoding="utf-8") as f:
        try:
            data: Dict[str, Any] = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {input_path}: {e}")
            sys.exit(1)

    # 3. Extract the list of samples from the top-level 'samples' key
    samples: List[Dict[str, Any]] = data.get("samples", [])
    if not isinstance(samples, list):
        print(f"Error: 'samples' key in {input_path} is not a list.")
        sys.exit(1)

    total_tests = len(samples)

    if total_tests == 0:
        print(f"No samples found in the result file: {input_path}")

    # 4. Correctly count tests based on the 'value' within scores.model_graded_qa
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

    # Calculate pass rate including both Complete and Partial grades
    passing_tests = passed_tests + partial_tests
    pass_rate = (passing_tests / total_tests) * 100 if total_tests > 0 else 0

    # Generate summary dictionary
    summary = {
        "total": total_tests,
        "passed": passed_tests,
        "partial": partial_tests,
        "failed": failed_tests,
        "pass_rate": pass_rate,
        "quality_gate_passed": pass_rate >= 80,  # 80% threshold
        "details": (
            f"Complete: {passed_tests}, Partial: {partial_tests}, "
            f"Incomplete: {failed_tests}, Passing: {passing_tests}/{total_tests}"
        ),
    }

    # 5. Save the summary in the same directory as the input file
    summary_file_path = input_path.parent / "summary.json"
    with open(summary_file_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nSummary saved to: {summary_file_path}")
    print(
        f"Processed {total_tests} tests: {passed_tests} complete, "
        f"{partial_tests} partial, {failed_tests} incomplete"
    )
    print(f"Pass rate (Complete + Partial): {pass_rate:.1f}%")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_results.py <path_to_result_file.json>")
        sys.exit(1)

    process_inspect_results(sys.argv[1])
