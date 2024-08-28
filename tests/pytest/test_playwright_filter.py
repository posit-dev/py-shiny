from __future__ import annotations

import glob
from pathlib import Path
from typing import Dict, Set

from tests.pytest._utils import skip_on_windows

known_entries: Dict[str, Set[str]] = {
    # "tests/pytest/test_poll.py": {
    #     "my_locator.filter('foo')",
    # }
}

# Trim all line values of `known_entries`
for k, v in known_entries.items():
    known_entries[k] = {x.strip() for x in v}


@skip_on_windows
def test_named_temporary_file_is_not_used():
    """
    Playwright's Locator hangs when we call `.filter(foo)`.
    Instead you should use `.locator("xpath=.", has=page.locator(foo))`
    """

    root_here = Path(__file__).parent.parent.parent
    shiny_files = glob.glob(str(root_here / "shiny" / "**" / "*.py"), recursive=True)
    tests_files = glob.glob(str(root_here / "tests" / "**" / "*.py"), recursive=True)

    assert len(shiny_files) > 0
    assert len(tests_files) > 0

    all_files = [*shiny_files, *tests_files]

    search_string = ".filter("

    bad_entries: list[tuple[Path, int, str]] = []

    # For every python file...
    for path in all_files:
        path = Path(path)
        # Skip if dir
        if path.is_dir():
            continue

        # Skip this file
        if path.name in {"test_playwright_filter.py"}:
            continue

        with open(path, "r") as f:
            # Read file contents
            txt = f.read().replace(".filter()", ".not_playwright_filter()")

            # Skip if search string is not in file
            if search_string not in txt:
                continue

            # Split file contents by line
            lines = txt.split("\n")
            rel_path = path.relative_to(root_here)
            known_lines = known_entries.get(str(rel_path), set())
            seen_lines: set[str] = set()

            # If the search string is in the line
            # and the line is not in the known lines,
            # add it to the bad entries
            for i, line in enumerate(lines):
                line = line.strip()
                if search_string in line:
                    seen_lines.add(line)
                    if line not in known_lines:
                        bad_entries.append((rel_path, i + 1, line))

            if (len(known_lines) > 0) and (len(seen_lines) != len(known_lines)):
                raise ValueError(
                    f"Lines not found in {rel_path}: {known_lines - seen_lines}"
                    "\nPlease remove them from the known_entries dictionary."
                )

    assert (
        len(bad_entries) == 0
    ), f"Unexpected files containing `.filter(`: {str(bad_entries)}"
