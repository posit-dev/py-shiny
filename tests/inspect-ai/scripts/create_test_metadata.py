import json
from itertools import islice
from pathlib import Path
from typing import Any, Dict, List, Union, cast

from shiny.pytest._generate import ShinyTestGenerator


def generate_shiny_test_metadata(
    apps_dir: Union[str, Path] = "tests/inspect-ai/apps", max_tests: int = 10
) -> Dict[str, Dict[str, Union[str, Path]]]:
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

    test_data: Dict[str, Dict[str, Union[str, Path]]] = {}

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
    test_data: Dict[str, Dict[str, Union[str, Path]]] = generate_shiny_test_metadata()

    metadata_file = Path(__file__).parent / "test_metadata.json"

    def convert_paths(obj: Any) -> Any:
        """Convert Path objects to strings for JSON serialization."""
        if isinstance(obj, dict):
            # Cast to Dict[Any, Any] to avoid type errors
            typed_dict = cast(Dict[Any, Any], obj)
            return {str(k): convert_paths(v) for k, v in typed_dict.items()}
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, list):
            # Cast to List[Any] to avoid type errors
            typed_list = cast(List[Any], obj)
            return [convert_paths(item) for item in typed_list]
        else:
            return obj

    serializable_test_data: Any = convert_paths(test_data)
    with open(metadata_file, "w") as f:
        json.dump(serializable_test_data, f, indent=2)

    print(f"Saved test metadata to: {metadata_file}")
