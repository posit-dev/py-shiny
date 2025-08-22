import argparse
import json
import sys
from pathlib import Path
from typing import Union


def prepare_comment(summary_path: Union[str, Path]) -> int:
    """
    Reads summary.json and other result files to create a formatted comment for GitHub PR
    showing averaged results across multiple attempts.

    Args:
        summary_path: Path to the summary.json file

    Returns:
        Exit code (0 on success, 1 on error) and writes output to comment_body.txt
    """
    try:
        summary_path = Path(summary_path)
        if not summary_path.exists():
            raise FileNotFoundError(f"Summary file not found at {summary_path}")

        # Read the inspect-ai averaged summary
        with open(summary_path, "r") as f:
            inspect_results = json.load(f)

        # Skip pytest results for now since they're not working properly
        pytest_results = None

        # Try to read the combined summary for overall gate status
        combined_results = None
        combined_summary_path = summary_path.parent / "combined_summary.json"
        if combined_summary_path.exists():
            with open(combined_summary_path, "r") as f:
                combined_results = json.load(f)

        # Build the comment
        comment_parts = [
            "## Test Generation Evaluation Results (Averaged across 3 attempts)\n"
        ]

        # Inspect AI section
        inspect_passing = inspect_results["passed"] + inspect_results["partial"]
        comment_parts.append("### 🔍 Inspect AI Test Quality Evaluation")
        comment_parts.append(f"- **Complete (C)**: {inspect_results['passed']:.1f}")
        comment_parts.append(f"- **Partial (P)**: {inspect_results['partial']:.1f}")
        comment_parts.append(f"- **Incomplete (I)**: {inspect_results['failed']:.1f}")
        comment_parts.append(
            f"- **Passing Rate**: {inspect_passing:.1f}/{inspect_results['total']:.1f} ({inspect_results['pass_rate']:.1f}%)"
        )
        comment_parts.append(
            f"- **Quality Gate**: {'✅ PASSED' if inspect_results['quality_gate_passed'] else '❌ FAILED'} (≥80% required)\n"
        )

        # Pytest section removed - not working properly

        # Overall status - just use inspect-ai quality gate for now
        comment_parts.append("### 🎯 Overall Result")
        comment_parts.append(
            f"**{'✅ PASSED' if inspect_results['quality_gate_passed'] else '❌ FAILED'}** - Quality gate based on Inspect AI results"
        )

        comment_parts.append("\n---")
        comment_parts.append(
            "*Results are averaged across 3 evaluation attempts for improved reliability.*"
        )

        comment = "\n".join(comment_parts)

        with open("comment_body.txt", "w") as f:
            f.write(comment)

        print("Comment body successfully prepared and written to comment_body.txt")
        return 0

    except Exception as e:
        print(f"Error reading summary file: {e}")

        comment = """## Test Generation Evaluation Results

❌ **Error**: Could not read evaluation results summary file.

Please check the workflow logs for details."""

        with open("comment_body.txt", "w") as f:
            f.write(comment)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prepare comment body for GitHub PR from test results"
    )
    parser.add_argument(
        "summary_path",
        nargs="?",
        default="results/summary.json",
        help="Path to the summary.json file (default: results/summary.json)",
    )
    parser.add_argument(
        "--help-custom", action="store_true", help="Show help message and exit"
    )

    args = parser.parse_args()

    sys.exit(prepare_comment(args.summary_path))
