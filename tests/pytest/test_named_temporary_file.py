from __future__ import annotations

import glob
from pathlib import Path
from typing import Dict, Set

# File names that contain `tempfile.NamedTemporaryFile` but are known to be correct.
# The key is the file name, the value is a set of lines stripped that contain `NamedTemporaryFile(`  that are known to be correct.
# This file (test_named_temporary_file.py) is automatically excluded.
known_entries: Dict[str, Set[str]] = {
    "tests/pytest/test_poll.py": {
        "tmpfile = tempfile.NamedTemporaryFile(delete=False)",
        "tmpfile1 = tempfile.NamedTemporaryFile(delete=False)",
    }
}

# Trim all line values of `known_entries`
for k, v in known_entries.items():
    known_entries[k] = {x.strip() for x in v}


def test_named_temporary_file_is_not_used():
    """
    Windows does not work well with tempfile.NamedTemporaryFile.

    * https://github.com/python/cpython/issues/58451
    * https://github.com/appveyor/ci/issues/2547
    * https://github.com/marickmanrho/pip-audit/commit/086ea4d684b41b795d9505b51ce7d079c990dca6
    * https://github.com/IdentityPython/pysaml2/pull/665/files
    * https://github.com/aws-cloudformation/cloudformation-cli/pull/924/files

    Fair fix:
    * Use a temp dir and create the file in the temp dir. On exit, the dir will be deleted.
        * https://stackoverflow.com/a/77536782/591574
    Possible future fix:
    * Related Issue: https://github.com/pypa/pip-audit/issues/646
    * Their fix: https://github.com/marickmanrho/pip-audit/commit/086ea4d684b41b795d9505b51ce7d079c990dca6#diff-a182a096790cc91a1771db39e19b337dec83c579775e46a45956a463b903b616
    """

    root_here = Path(__file__).parent.parent.parent

    dir_content = [
        *glob.glob("shiny/**/*.py", root_dir=root_here, recursive=True),
        *glob.glob("tests/**/*.py", root_dir=root_here, recursive=True),
    ]

    search_string = "NamedTemporaryFile("

    bad_entries: list[tuple[str, int, str]] = []

    # For every python file...
    for p in dir_content:
        path = Path(root_here, p)
        # Skip if dir
        if path.is_dir():
            continue

        # Skip this file
        if path.name in {"test_named_temporary_file.py"}:
            continue

        with open(path, "r") as f:
            # Read file contents
            txt = f.read()

            # Skip if search string is not in file
            if search_string not in txt:
                continue

            # Split file contents by line
            lines = txt.split("\n")
            known_lines = known_entries.get(str(p), set())

            # If the search string is in the line
            # and the line is not in the known lines,
            # add it to the bad entries
            for i, line in enumerate(lines):
                line = line.strip()
                if search_string in line and (line not in known_lines):
                    bad_entries.append((p, i + 1, line))

    assert (
        len(bad_entries) == 0
    ), f"Unexpected files containing `TemporaryDirectory`: {str(bad_entries)}"
