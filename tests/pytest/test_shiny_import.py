from __future__ import annotations

import glob
from pathlib import Path

from tests.pytest._utils import skip_on_windows


class BadLine:
    def __init__(self, path: Path, line_number: int, line_text: str):
        self.path = path
        self.line_number = line_number
        self.line_text = line_text

    def __repr__(self):
        return f"{self.path}:{self.line_number} - {self.line_text}"


@skip_on_windows
def test_shiny_import_itself():
    """
    VSCode likes to import from the shiny module itself within the shiny package. While it works... it relies on import magic, not relative imports.

    Bad: `from shiny import ui`
    Good: `from . import ui`
    """

    root_here = Path(__file__).parent.parent.parent
    shiny_files = glob.glob(str(root_here / "shiny" / "**" / "*.py"), recursive=True)

    shiny_files = [
        path
        for path in shiny_files
        if "/api-examples/" not in path
        and "/templates/" not in path
        and Path(path).is_file()
    ]

    assert len(shiny_files) > 0

    # bad_entries: list[tuple[Path, int, str]] = []
    bad_entries: list[BadLine] = []

    # For every python file...
    for path in shiny_files:
        path = Path(path)

        file_txt = path.read_text(encoding="utf-8")
        while True:
            if "\ndef " in file_txt:
                file_txt = file_txt.split("\ndef ")[0]
            elif "\nasync def " in file_txt:
                file_txt = file_txt.split("\nasync def ")[0]
            elif "\nclass " in file_txt:
                file_txt = file_txt.split("\nclass ")[0]
            else:
                break

        for search_txt in ("\nfrom shiny.", "\nfrom shiny ", "\nimport shiny\n"):
            if search_txt == "\nimport shiny\n" and path.name.endswith("_main.py"):
                # skip shiny/_main.py file
                continue

            if search_txt in file_txt:

                for i, line in enumerate(file_txt.split("\n")):
                    if line.startswith(search_txt.strip()):
                        # bad_entries.append((path.relative_to(root_here), i + 1, line))
                        bad_entries.append(
                            BadLine(path.relative_to(root_here), i + 1, line)
                        )

    if len(bad_entries) > 0:
        print("Bad entries found:")
        for entry in bad_entries:
            print(entry)
    # Ensure no bad entries exist
    assert (
        len(bad_entries) == 0
    ), "Unexpected shiny files containing `from shiny.FOO import BAR`, `from shiny import FOO`, or `import shiny`"
