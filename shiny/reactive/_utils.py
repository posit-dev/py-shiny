"""
Internal utilities for the reactive module.

This module contains helper functions used by reactive classes.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ("is_user_code_frame",)


def is_user_code_frame(filename: str) -> bool:
    """
    Check if a filename represents user code (not internal shiny package code).

    This is used by stack inspection code to filter out internal shiny frames
    and find the first frame of user code.

    Parameters
    ----------
    filename
        Path to the file to check

    Returns
    -------
    bool
        True if the file is user code, False if it's internal shiny code

    Examples
    --------
    >>> is_user_code_frame("/home/user/app.py")
    True
    >>> is_user_code_frame("/usr/lib/python/site-packages/shiny/reactive/_reactives.py")
    False
    >>> is_user_code_frame("/usr/lib/python/site-packages/shiny/tests/test_reactive.py")
    True

    Notes
    -----
    The function considers these as user code:
    - Any file outside the shiny package
    - Test files (files starting with "test_")
    - Files in the shiny/tests directory

    The function filters out:
    - Special/generated frames (filename starts with "<")
    - Internal shiny package code (except tests)
    """
    # Skip special/generated frames
    if not filename or filename.startswith("<"):
        return False

    # Test files are always considered user code
    file_path = Path(filename)
    if file_path.name.startswith("test_"):
        return True

    # Check if file is within shiny package directory
    try:
        # Get the shiny package directory (two levels up from this file)
        # This file is at shiny/reactive/_utils.py, so we go up to shiny/
        shiny_package_dir = Path(__file__).parent.parent

        # Check if file is under shiny package
        if file_path.is_relative_to(shiny_package_dir):
            # Allow tests and examples
            if not (
                file_path.is_relative_to(shiny_package_dir / "examples")
                or file_path.is_relative_to(shiny_package_dir / "tests")
                or file_path.is_relative_to(
                    shiny_package_dir / "shiny" / "api-examples"
                )
            ):
                return True

            return False

    except (ValueError, TypeError):
        # Different drives on Windows or other path issues - treat as user code
        pass

    return True
