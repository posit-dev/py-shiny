import argparse
import json
import sys
from pathlib import Path
from typing import Union


def prepare_comment(summary_path: Union[str, Path]) -> int:
    """
    Reads summary.json and creates a formatted comment for GitHub PR.

    Args:
        summary_path: Path to the summary.json file

    Returns:
        Exit code (0 on success, 1 on error) and writes output to comment_body.txt
    """
    try:
        summary_path = Path(summary_path)
        if not summary_path.exists():
            raise FileNotFoundError(f"Summary file not found at {summary_path}")

        with open(summary_path, "r") as f:
            results = json.load(f)

        comment = f"""## Inspect AI Evaluation Results

- **Tests Passed**: {results['passed']}/{results['total']}
- **Quality Gate**: {'✅ PASSED' if results['quality_gate_passed'] else '❌ FAILED'}

### Details
{results['details']}
"""

        with open("comment_body.txt", "w") as f:
            f.write(comment)

        print("Comment body successfully prepared and written to comment_body.txt")
        return 0

    except Exception as e:
        print(f"Error reading summary file: {e}")

        comment = """## Inspect AI Evaluation Results

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
