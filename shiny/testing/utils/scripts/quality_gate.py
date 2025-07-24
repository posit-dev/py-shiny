import json
import sys
from pathlib import Path


def check_quality_gate(results_dir, threshold=80):
    """Check if evaluation results meet quality gate"""
    summary_path = Path(results_dir) / "summary.json"

    if not summary_path.exists():
        print("Summary file not found")
        sys.exit(1)

    with open(summary_path, "r") as f:
        summary = json.load(f)

    pass_rate = summary.get("pass_rate", 0)

    if pass_rate >= threshold:
        print(f"✅ Quality gate PASSED: {pass_rate:.1f}% >= {threshold}%")
        sys.exit(0)
    else:
        print(f"❌ Quality gate FAILED: {pass_rate:.1f}% < {threshold}%")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quality_gate.py <results_dir>")
        sys.exit(1)

    check_quality_gate(sys.argv[1])
