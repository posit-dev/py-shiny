import json
from itertools import islice
from pathlib import Path

from shiny.pytest._generate import ShinyTestGenerator


def generate_shiny_test_metadata(
    apps_dir: str | Path = "tests/inspect-ai/apps", max_tests: int = 10
) -> dict:
    """
    Generate Shiny tests and metadata for apps in the specified directory.

    Args:
        apps_dir: Directory containing Shiny apps
        max_tests: Maximum number of tests to generate

    Returns:
        Dictionary mapping test names to test metadata including code and app info
    """
    generator = ShinyTestGenerator()
    apps_dir = Path(apps_dir)

    if not apps_dir.exists() and apps_dir.is_relative_to("."):
        script_dir = Path(__file__).parent
        apps_dir = script_dir.parent / "apps"
        if not apps_dir.exists():
            apps_dir = script_dir.parent.parent.parent / "tests" / "inspect-ai" / "apps"

    app_files = islice(apps_dir.glob("*/app*.py"), max_tests)

    test_data = {}

    for app_path in app_files:
        try:
            test_code, test_file_path = generator.generate_test_from_file(str(app_path))

            test_name = f"test_{app_path.parent.name}_{app_path.stem}"
            app_code = app_path.read_text(encoding="utf-8")

            test_data[test_name] = {
                "test_code": test_code,
                "app_code": app_code,
                "app_path": str(app_path),
                "test_file_path": test_file_path,
                "app_name": app_path.parent.name,
            }

        except Exception as e:
            print(f"Error generating test for {app_path}: {e}")
            continue

    return test_data


if __name__ == "__main__":
    test_data = generate_shiny_test_metadata()

    metadata_file = Path(__file__).parent / "test_metadata.json"

    def convert_paths(obj):
        if isinstance(obj, dict):
            return {k: convert_paths(v) for k, v in obj.items()}
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, list):
            return [convert_paths(i) for i in obj]
        else:
            return obj

    serializable_test_data = convert_paths(test_data)
    with open(metadata_file, "w") as f:
        json.dump(serializable_test_data, f, indent=2)

    print(f"Saved test metadata to: {metadata_file}")
